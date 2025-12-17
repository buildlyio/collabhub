#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Only set default to dev if DJANGO_SETTINGS_MODULE is not already configured
    # This allows production deployments to set it explicitly and override it
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
        # Only enforce local dev guard when using the dev default
        if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("production"):
            sys.stderr.write(
                "Refusing to run with production settings from this entrypoint. "
                "Set DJANGO_SETTINGS_MODULE explicitly if you intentionally need this.\n"
            )
            sys.exit(1)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
