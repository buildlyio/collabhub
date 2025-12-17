#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Default to dev settings locally; block accidental production usage from local runs
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")

    # Only enforce the guard in local/dev environments, not in production deployments
    # Production deployments should have RUN_MODE=production or be deployed via CI/CD
    is_local_dev = not os.environ.get("RUN_MODE") or os.environ.get("RUN_MODE") == "dev"
    
    if (
        is_local_dev
        and settings_module.endswith("production")
        and not os.environ.get("ALLOW_PROD_FROM_LOCAL")
    ):
        sys.stderr.write(
            "Refusing to run with production settings from this entrypoint. "
            "Set ALLOW_PROD_FROM_LOCAL=1 if you intentionally need this.\n"
        )
        sys.exit(1)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
