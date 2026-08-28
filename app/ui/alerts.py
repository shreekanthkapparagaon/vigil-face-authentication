from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AlertDialog(QDialog):
    """Futuristic application alert dialog."""

    def __init__(
        self,
        title: str,
        message: str,
        alert_type: str = "info",
        parent: QWidget | None = None,
        button_text: str = "OK",
    ) -> None:
        super().__init__(parent)

        self.alert_type = alert_type

        self.setObjectName("alertDialog")
        self.setProperty("alertType", alert_type)

        self.setWindowTitle(title)
        self.setModal(True)

        self.setMinimumWidth(440)
        self.setMaximumWidth(600)

        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        self._setup_ui(
            title=title,
            message=message,
            button_text=button_text,
        )

        self._refresh_style()

    # =====================================================
    # UI
    # =====================================================

    def _setup_ui(
        self,
        title: str,
        message: str,
        button_text: str,
    ) -> None:
        """Build the alert interface."""

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            22,
            24,
            20,
        )

        layout.setSpacing(14)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        header_layout.setSpacing(14)

        self.icon_label = QLabel(
            self._get_icon()
        )

        self.icon_label.setObjectName(
            "alertIcon"
        )

        self.icon_label.setFixedWidth(42)

        self.icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_layout.addWidget(
            self.icon_label
        )

        title_layout = QVBoxLayout()

        title_layout.setSpacing(3)

        self.title_label = QLabel(
            title
        )

        self.title_label.setObjectName(
            "alertTitle"
        )

        self.title_label.setWordWrap(
            True
        )

        title_layout.addWidget(
            self.title_label
        )

        self.type_label = QLabel(
            self._get_type_label()
        )

        self.type_label.setObjectName(
            "alertTypeLabel"
        )

        title_layout.addWidget(
            self.type_label
        )

        header_layout.addLayout(
            title_layout,
            stretch=1,
        )

        layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Divider
        # -------------------------------------------------

        divider = QWidget()

        divider.setObjectName(
            "neonDivider"
        )

        divider.setFixedHeight(
            1
        )

        layout.addWidget(
            divider
        )

        # -------------------------------------------------
        # Message
        # -------------------------------------------------

        self.message_label = QLabel(
            message
        )

        self.message_label.setObjectName(
            "alertMessage"
        )

        self.message_label.setWordWrap(
            True
        )

        self.message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout.addWidget(
            self.message_label
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        self.ok_button = QPushButton(
            button_text
        )

        self.ok_button.setObjectName(
            "alertPrimaryButton"
        )

        self.ok_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.ok_button.setMinimumWidth(
            90
        )

        self.ok_button.clicked.connect(
            self.accept
        )

        buttons_layout.addWidget(
            self.ok_button
        )

        layout.addLayout(
            buttons_layout
        )

    # =====================================================
    # Helpers
    # =====================================================

    def _get_icon(self) -> str:
        """Return an icon based on alert type."""

        icons = {
            "info": "ⓘ",
            "success": "✓",
            "warning": "⚠",
            "error": "×",
            "authenticated": "✓",
            "authentication_failed": "×",
            "camera": "◉",
        }

        return icons.get(
            self.alert_type,
            "ⓘ",
        )

    def _get_type_label(self) -> str:
        """Return a technical label for the alert."""

        labels = {
            "info": "SYSTEM INFORMATION",
            "success": "OPERATION COMPLETE",
            "warning": "SYSTEM WARNING",
            "error": "SYSTEM ERROR",
            "authenticated": "IDENTITY VERIFIED",
            "authentication_failed": "IDENTITY REJECTED",
            "camera": "CAMERA SYSTEM",
        }

        return labels.get(
            self.alert_type,
            "SYSTEM MESSAGE",
        )

    def _refresh_style(self) -> None:
        """Refresh Qt dynamic-property styling."""

        self.style().unpolish(
            self
        )

        self.style().polish(
            self
        )

        self.update()


# =========================================================
# Public alert helpers
# =========================================================


def show_alert(
    parent: QWidget | None,
    title: str,
    message: str,
    alert_type: str = "info",
    button_text: str = "OK",
) -> None:
    """Display a standard application alert."""

    dialog = AlertDialog(
        title=title,
        message=message,
        alert_type=alert_type,
        parent=parent,
        button_text=button_text,
    )

    dialog.exec()


def show_info(
    parent: QWidget | None,
    title: str,
    message: str,
) -> None:
    """Display an information alert."""

    show_alert(
        parent=parent,
        title=title,
        message=message,
        alert_type="info",
    )


def show_success(
    parent: QWidget | None,
    title: str,
    message: str,
) -> None:
    """Display a success alert."""

    show_alert(
        parent=parent,
        title=title,
        message=message,
        alert_type="success",
    )


def show_warning(
    parent: QWidget | None,
    title: str,
    message: str,
) -> None:
    """Display a warning alert."""

    show_alert(
        parent=parent,
        title=title,
        message=message,
        alert_type="warning",
    )


def show_error(
    parent: QWidget | None,
    title: str,
    message: str,
) -> None:
    """Display an error alert."""

    show_alert(
        parent=parent,
        title=title,
        message=message,
        alert_type="error",
    )


def show_authenticated(
    parent: QWidget | None,
    user_name: str,
    similarity: float | None = None,
) -> None:
    """Display successful face authentication."""

    if similarity is not None:
        message = (
            f"Identity confirmed for {user_name}.\n\n"
            f"Face similarity: {similarity:.1%}"
        )
    else:
        message = (
            f"Identity confirmed for {user_name}."
        )

    show_alert(
        parent=parent,
        title="Authentication Successful",
        message=message,
        alert_type="authenticated",
    )


def show_authentication_failed(
    parent: QWidget | None,
    message: str = "The face could not be matched to a registered user.",
) -> None:
    """Display failed face authentication."""

    show_alert(
        parent=parent,
        title="Authentication Failed",
        message=message,
        alert_type="authentication_failed",
    )


def show_camera_error(
    parent: QWidget | None,
    message: str,
) -> None:
    """Display a camera-related error."""

    show_alert(
        parent=parent,
        title="Camera Error",
        message=message,
        alert_type="camera",
    )


# =========================================================
# Exception handling
# =========================================================


def show_exception(
    parent: QWidget | None,
    title: str,
    exc: Exception,
    fallback_message: str = "An unexpected error occurred.",
) -> None:
    """
    Display an exception safely without exposing a traceback
    to the normal application user.
    """

    message = str(exc).strip()

    if not message:
        message = fallback_message

    show_error(
        parent=parent,
        title=title,
        message=message,
    )


def run_with_alert(
    parent: QWidget | None,
    operation: Callable[[], object],
    title: str = "Operation Failed",
) -> object | None:
    """
    Execute an operation and convert unexpected exceptions
    into a user-friendly alert.

    Returns:
        Operation result on success.
        None when an exception occurs.
    """

    try:
        return operation()

    except Exception as exc:
        show_exception(
            parent=parent,
            title=title,
            exc=exc,
        )

        return None