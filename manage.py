#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Default to dev settings locally; block accidental production usage from local runs
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")

    if settings_module.endswith("production") and not os.environ.get("ALLOW_PROD_FROM_LOCAL"):
        sys.stderr.write(
            "Refusing to run with production settings from this entrypoint. "
            "Set ALLOW_PROD_FROM_LOCAL=1 if you intentionally need this.\n"
        )
        sys.exit(1)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
