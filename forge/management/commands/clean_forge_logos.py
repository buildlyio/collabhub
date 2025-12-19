from django.core.management.base import BaseCommand
from forge.models import ForgeApp
import requests
import time


class Command(BaseCommand):
    help = "Validate ForgeApp.logo_url and clear invalid ones (uses default fallback in UI)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true', help='Only report invalid URLs without modifying data'
        )
        parser.add_argument(
            '--timeout', type=float, default=3.0, help='HTTP timeout in seconds for URL checks'
        )
        parser.add_argument(
            '--sleep', type=float, default=0.0, help='Sleep seconds between requests to be gentle on hosts'
        )

    def url_ok(self, url: str, timeout: float = 3.0) -> bool:
        if not url:
            return False
        try:
            r = requests.head(url, allow_redirects=True, timeout=timeout)
            if r.status_code == 200:
                return True
            if r.status_code in (405, 403):
                r = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
                return r.status_code == 200
            return False
        except requests.RequestException:
            return False

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        timeout = options['timeout']
        sleep_s = options['sleep']

        total = ForgeApp.objects.count()
        checked = 0
        invalid = 0
        fixed = 0

        self.stdout.write(self.style.NOTICE(
            f"Scanning {total} Forge apps for invalid logo URLs (dry_run={dry_run})"
        ))

        for app in ForgeApp.objects.all():
            checked += 1
            url = app.logo_url
            if url:
                ok = self.url_ok(url, timeout=timeout)
                if not ok:
                    invalid += 1
                    self.stdout.write(f"Invalid: {app.slug} -> {url}")
                    if not dry_run:
                        app.logo_url = None
                        app.save(update_fields=['logo_url'])
                        fixed += 1
            if sleep_s:
                time.sleep(sleep_s)

        summary = f"Checked: {checked}, Invalid: {invalid}, Fixed: {fixed}"
        if fixed > 0 and not dry_run:
            self.stdout.write(self.style.SUCCESS(summary))
        else:
            self.stdout.write(summary)
