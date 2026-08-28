from __future__ import annotations

import sys
import traceback

from PyQt6.QtWidgets import QApplication

from app.ui.alerts import show_error
from app.ui.main_window import MainWindow
from app.ui.styles import get_app_stylesheet


def main() -> int:
    """Application entry point."""

    application = QApplication(
        sys.argv
    )

    application.setApplicationName(
        "Face Authentication"
    )

    application.setStyleSheet(
        get_app_stylesheet()
    )

    window = MainWindow()

    window.show()

    return application.exec()


def install_exception_handler(
    application: QApplication,
) -> None:
    """Install a global exception handler."""

    def handle_exception(
        exc_type,
        exc_value,
        exc_traceback,
    ) -> None:
        if exc_type is KeyboardInterrupt:
            sys.__excepthook__(
                exc_type,
                exc_value,
                exc_traceback,
            )
            return

        # Keep the traceback in the terminal for debugging.
        traceback.print_exception(
            exc_type,
            exc_value,
            exc_traceback,
        )

        message = str(
            exc_value
        ).strip()

        if not message:
            message = (
                "An unexpected error occurred "
                "inside the application."
            )

        # Find the active window.
        parent = None

        for widget in application.topLevelWidgets():
            if widget.isVisible():
                parent = widget
                break

        show_error(
            parent,
            "Unexpected Application Error",
            (
                f"{message}\n\n"
                "The error has been reported to "
                "the application console."
            ),
        )

    sys.excepthook = handle_exception


if __name__ == "__main__":
    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Face Authentication"
    )

    app.setStyleSheet(
        get_app_stylesheet()
    )

    install_exception_handler(
        app
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )