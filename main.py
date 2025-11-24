"""Main entry point for CleanUp application."""

import sys
from app import CleanUpApp


def main():
    """Launch the CleanUp application."""
    app = CleanUpApp(sys.argv)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

