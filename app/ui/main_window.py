from __future__ import annotations

import time
import uuid
from pathlib import Path
from PyQt6.QtGui import QIcon

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.config import settings
from app.schemas.user import UserCreate
from app.services.face_auth import FaceAuthService
from app.ui.camera_widget import CameraWidget


class MainWindow(QMainWindow):
    """Main futuristic face authentication application."""

    def __init__(
        self,
        face_auth_service: FaceAuthService | None = None,
    ) -> None:
        super().__init__()
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parent.parent / "assets" / "icon.ico")))

        self.face_auth_service = (
            face_auth_service
            or FaceAuthService()
        )

        # IMPORTANT:
        # Reuse the same FaceEngine for both cameras.
        self.face_engine = (
            self.face_auth_service.face_engine
        )

        self.setWindowTitle(
            settings.app_name
        )

        self.setMinimumSize(
            1180,
            720,
        )

        self.resize(
            1400,
            850,
        )

        self._navigation_buttons: dict[
            str,
            QPushButton,
        ] = {}

        # -------------------------------------------------
        # Registration state.
        # -------------------------------------------------

        self._enrollment_active = False
        self._enrollment_frames = []
        self._last_enrollment_capture = 0.0

        self._setup_ui()

        self._refresh_dashboard()
        self._refresh_users()

        self._show_page(
            "Dashboard"
        )

    # =====================================================
    # Main UI
    # =====================================================
    def _setup_ui(self) -> None:
        """Build main application shell."""

        central = QWidget()
        central.setObjectName("mainCentralWidget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self._create_sidebar()

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")

        self.dashboard_page = self._create_dashboard_page()
        self.register_page = self._create_register_page()
        self.authenticate_page = self._create_authenticate_page()
        self.users_page = self._create_users_page()
        self.settings_page = self._create_settings_page()

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.register_page)
        self.content_stack.addWidget(self.authenticate_page)
        self.content_stack.addWidget(self.users_page)
        self.content_stack.addWidget(self.settings_page)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, stretch=1)

        root_layout.addLayout(main_layout, stretch=1)
        root_layout.addWidget(self._create_application_footer())
    
    # =====================================================
    # Sidebar
    # =====================================================
    def _create_sidebar(self) -> QFrame:
        """Create futuristic navigation."""

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            250
        )

        layout = QVBoxLayout(
            sidebar
        )

        layout.setContentsMargins(
            22,
            26,
            22,
            22,
        )

        layout.setSpacing(
            7
        )

        # -------------------------------------------------
        # Brand.
        # -------------------------------------------------

        brand_layout = QVBoxLayout()

        brand = QLabel(
            "VIGIL"
        )

        brand.setObjectName(
            "brandTitle"
        )

        brand_subtitle = QLabel(
            "BIOMETRIC SECURITY"
        )

        brand_subtitle.setObjectName(
            "brandSubtitle"
        )

        brand_layout.addWidget(
            brand
        )

        brand_layout.addWidget(
            brand_subtitle
        )

        layout.addLayout(
            brand_layout
        )

        # System indicator.
        system_status = QLabel(
            "● SYSTEM ONLINE"
        )

        system_status.setObjectName(
            "systemStatus"
        )

        layout.addWidget(
            system_status
        )

        layout.addSpacing(
            28
        )

        # -------------------------------------------------
        # Navigation.
        # -------------------------------------------------

        navigation_items = [
            (
                "Dashboard",
                "OVERVIEW",
            ),
            (
                "Register User",
                "ENROLLMENT",
            ),
            (
                "Authenticate",
                "IDENTITY SCAN",
            ),
            (
                "Users",
                "IDENTITY DATABASE",
            ),
            (
                "Settings",
                "SYSTEM CONFIG",
            ),
        ]

        for name, subtitle in navigation_items:
            button = QPushButton(
                f"  {name.upper()}"
            )

            button.setObjectName(
                "sidebarButton"
            )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setMinimumHeight(
                46
            )

            button.setToolTip(
                subtitle
            )

            button.clicked.connect(
                lambda checked=False,
                page=name: self._show_page(page)
            )

            self._navigation_buttons[
                name
            ] = button

            layout.addWidget(
                button
            )

        layout.addStretch()

        # -------------------------------------------------
        # Bottom system info.
        # -------------------------------------------------

        line = QFrame()

        line.setObjectName(
            "sidebarDivider"
        )

        line.setFixedHeight(
            1
        )

        layout.addWidget(
            line
        )

        version = QLabel(
            "VIGIL FACE AUTHENTICATION\n"
            "CORE SYSTEM v1.0.0"
        )

        version.setObjectName(
            "sidebarVersion"
        )

        layout.addWidget(
            version
        )

        return sidebar

    # =====================================================
    # Common page header
    # =====================================================
    def _create_page_header(
        self,
        title: str,
        subtitle: str,
        code: str | None = None,
    ) -> QVBoxLayout:
        """Create a consistent futuristic page header."""

        layout = QVBoxLayout()

        layout.setSpacing(
            5
        )

        # -------------------------------------------------
        # Optional page code / breadcrumb
        # -------------------------------------------------

        if code:
            code_label = QLabel(
                f"// {code}"
            )

            code_label.setObjectName(
                "pageCode"
            )

            layout.addWidget(
                code_label
            )

        # -------------------------------------------------
        # Page title
        # -------------------------------------------------

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "pageTitle"
        )

        layout.addWidget(
            title_label
        )

        # -------------------------------------------------
        # Page subtitle
        # -------------------------------------------------

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setObjectName(
            "pageSubtitle"
        )

        layout.addWidget(
            subtitle_label
        )

        return layout

    # =====================================================
    # Dashboard
    # =====================================================
    def _create_dashboard_page(self) -> QWidget:
        """Create the system dashboard."""
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(16)

        layout.addLayout(self._create_page_header(
            "SYSTEM OVERVIEW",
            "Biometric authentication control center",
        ))

        # System summary
        summary_card = QFrame()
        summary_card.setObjectName("contentCard")

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(22, 16, 22, 16)
        summary_layout.setSpacing(30)

        self.dashboard_users_value = QLabel("0")
        self.dashboard_users_value.setObjectName("statValue")

        self.dashboard_auth_value = QLabel("READY")
        self.dashboard_auth_value.setObjectName("statusOnline")

        self.dashboard_camera_value = QLabel("STANDBY")
        self.dashboard_camera_value.setObjectName("statusInfo")

        self.dashboard_security_value = QLabel("ACTIVE")
        self.dashboard_security_value.setObjectName("statusOnline")

        summary_items = [
            ("REGISTERED IDENTITIES", self.dashboard_users_value, "Biometric profiles"),
            ("AUTHENTICATION ENGINE", self.dashboard_auth_value, "SFace recognition"),
            ("VISION SENSOR", self.dashboard_camera_value, "Camera subsystem"),
            ("SECURITY STATUS", self.dashboard_security_value, "Verification service"),
        ]

        for title, value, description in summary_items:
            item = QWidget()

            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(2)

            title_label = QLabel(title)
            title_label.setObjectName("statTitle")

            description_label = QLabel(description)
            description_label.setObjectName("statDescription")

            item_layout.addWidget(title_label)
            item_layout.addWidget(value)
            item_layout.addWidget(description_label)

            summary_layout.addWidget(item, stretch=1)

        layout.addWidget(summary_card)

        # Quick actions
        command_card = QFrame()
        command_card.setObjectName("contentCard")

        command_layout = QVBoxLayout(command_card)
        command_layout.setContentsMargins(22, 18, 22, 18)
        command_layout.setSpacing(8)

        command_title = QLabel("BIOMETRIC CONTROL")
        command_title.setObjectName("cardTitle")

        command_text = QLabel(
            "Start an operation or manage registered identities."
        )
        command_text.setObjectName("cardText")

        command_layout.addWidget(command_title)
        command_layout.addWidget(command_text)

        actions = QHBoxLayout()
        actions.setSpacing(10)

        authenticate_button = QPushButton("◉  START AUTHENTICATION")
        authenticate_button.setObjectName("primaryButton")
        authenticate_button.setMinimumHeight(42)
        authenticate_button.clicked.connect(
            lambda: self._show_page("Authenticate")
        )

        register_button = QPushButton("＋  REGISTER IDENTITY")
        register_button.setObjectName("secondaryButton")
        register_button.setMinimumHeight(42)
        register_button.clicked.connect(
            lambda: self._show_page("Register User")
        )

        users_button = QPushButton("▣  MANAGE IDENTITIES")
        users_button.setObjectName("secondaryButton")
        users_button.setMinimumHeight(42)
        users_button.clicked.connect(
            lambda: self._show_page("Users")
        )

        settings_button = QPushButton("⚙  SYSTEM SETTINGS")
        settings_button.setObjectName("secondaryButton")
        settings_button.setMinimumHeight(42)
        settings_button.clicked.connect(
            lambda: self._show_page("Settings")
        )

        actions.addWidget(authenticate_button)
        actions.addWidget(register_button)
        actions.addWidget(users_button)
        actions.addWidget(settings_button)
        actions.addStretch()

        command_layout.addLayout(actions)
        layout.addWidget(command_card)

        # Information grid
        information_layout = QHBoxLayout()
        information_layout.setSpacing(14)

        # System diagnostics
        diagnostics = QFrame()
        diagnostics.setObjectName("contentCard")

        diagnostics_layout = QVBoxLayout(diagnostics)
        diagnostics_layout.setContentsMargins(22, 18, 22, 18)
        diagnostics_layout.setSpacing(8)

        diagnostics_title = QLabel("SYSTEM DIAGNOSTICS")
        diagnostics_title.setObjectName("cardTitle")

        diagnostics_description = QLabel(
            "Current runtime state of core biometric services."
        )
        diagnostics_description.setObjectName("cardText")
        diagnostics_description.setWordWrap(True)

        diagnostics_layout.addWidget(diagnostics_title)
        diagnostics_layout.addWidget(diagnostics_description)

        diagnostics_grid = QGridLayout()
        diagnostics_grid.setContentsMargins(0, 4, 0, 0)
        diagnostics_grid.setHorizontalSpacing(20)
        diagnostics_grid.setVerticalSpacing(7)
        diagnostics_grid.setColumnStretch(0, 1)
        diagnostics_grid.setColumnStretch(1, 1)

        diagnostic_items = [
            ("Face detector", "ONLINE", "statusOnline"),
            ("Recognition engine", "ONLINE", "statusOnline"),
            ("Database", "CONNECTED", "statusOnline"),
            ("Embedding cache", "READY", "statusOnline"),
            ("Authentication service", "READY", "statusOnline"),
            ("Camera subsystem", "STANDBY", "statusInfo"),
        ]

        self.dashboard_diagnostic_values = {}

        for row, (label_text, value_text, object_name) in enumerate(
            diagnostic_items
        ):
            label = QLabel(label_text)
            label.setObjectName("fieldLabel")
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

            value = QLabel(f"●  {value_text}")
            value.setObjectName(object_name)
            value.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

            diagnostics_grid.addWidget(label, row, 0)
            diagnostics_grid.addWidget(value, row, 1)

            self.dashboard_diagnostic_values[label_text] = value

        diagnostics_layout.addLayout(diagnostics_grid)

        information_layout.addWidget(diagnostics, stretch=1)

        # Engine information
        engine_card = QFrame()
        engine_card.setObjectName("contentCard")

        engine_layout = QVBoxLayout(engine_card)
        engine_layout.setContentsMargins(22, 18, 22, 18)
        engine_layout.setSpacing(8)

        engine_title = QLabel("ENGINE INFORMATION")
        engine_title.setObjectName("cardTitle")

        engine_description = QLabel(
            "Active biometric processing configuration."
        )
        engine_description.setObjectName("cardText")
        engine_description.setWordWrap(True)

        engine_layout.addWidget(engine_title)
        engine_layout.addWidget(engine_description)

        engine_grid = QGridLayout()
        engine_grid.setContentsMargins(0, 4, 0, 0)
        engine_grid.setHorizontalSpacing(20)
        engine_grid.setVerticalSpacing(7)
        engine_grid.setColumnStretch(0, 1)
        engine_grid.setColumnStretch(1, 1)

        engine_items = [
            ("Face detector", "YuNet"),
            ("Recognition model", "SFace"),
            ("Matching method", "Cosine similarity"),
            ("Detection scale", f"{settings.face_detection_scale:.2f}"),
            ("Match threshold", f"{settings.face_match_threshold:.3f}"),
            ("Processing mode", "Real-time"),
        ]

        for row, (label_text, value_text) in enumerate(engine_items):
            label = QLabel(label_text)
            label.setObjectName("fieldLabel")
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

            value = QLabel(value_text)
            value.setObjectName("settingValue")
            value.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

            engine_grid.addWidget(label, row, 0)
            engine_grid.addWidget(value, row, 1)

        engine_layout.addLayout(engine_grid)

        information_layout.addWidget(engine_card, stretch=1)
        layout.addLayout(information_layout)

        # Security
        security_card = QFrame()
        security_card.setObjectName("contentCard")

        security_layout = QHBoxLayout(security_card)
        security_layout.setContentsMargins(22, 14, 22, 14)
        security_layout.setSpacing(18)

        security_title = QLabel("SECURITY")
        security_title.setObjectName("cardTitle")

        security_status = QLabel(
            "●  BIOMETRIC VERIFICATION ACTIVE"
        )
        security_status.setObjectName("statusOnline")

        security_description = QLabel(
            "Local authentication • Protected embeddings • Database online"
        )
        security_description.setObjectName("cardText")

        security_layout.addWidget(security_title)
        security_layout.addWidget(security_status)
        security_layout.addWidget(security_description)
        security_layout.addStretch()

        layout.addWidget(security_card)
        layout.addStretch()

        return page


    # =====================================================
    # Dashboard Statistic Card
    # =====================================================
    def _create_stat_card(self, title: str, value: str, description: str) -> QFrame:
        """Create a compact statistic card."""
        card = QFrame()
        card.setObjectName("contentCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(3)

        label = QLabel(title)
        label.setObjectName("statTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        description_label = QLabel(description)
        description_label.setObjectName("statDescription")
        description_label.setWordWrap(True)

        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)

        card.value_label = value_label
        return card    
    
   
    # =====================================================
    # Registration
    # =====================================================
    def _generate_user_code(self) -> str:
        """Generate a unique user code."""

        while True:
            code = f"USR-{uuid.uuid4().hex[:6].upper()}"

            users = self.face_auth_service.list_users(
                search=code
            )

            if not users:
                return code
        
    def _create_register_page(self) -> QWidget:
        """Create biometric enrollment page."""

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            38,
            30,
            38,
            30,
        )

        layout.setSpacing(
            16
        )

        layout.addLayout(
            self._create_page_header(
                "REGISTER IDENTITY",
                "Create a biometric profile using multiple face samples",
            )
        )

        content = QHBoxLayout()

        content.setSpacing(
            18
        )

        # -------------------------------------------------
        # Camera.
        # -------------------------------------------------

        self.register_camera = CameraWidget(
            face_engine=self.face_engine
        )

        self.register_camera.frame_captured.connect(
            self._on_registration_frame
        )

        content.addWidget(
            self.register_camera,
            stretch=2,
        )

        # -------------------------------------------------
        # Registration form.
        # -------------------------------------------------

        form_card = QFrame()

        form_card.setObjectName(
            "contentCard"
        )

        form_card.setMinimumWidth(
            330
        )

        form_layout = QVBoxLayout(
            form_card
        )

        form_layout.setContentsMargins(
            22,
            22,
            22,
            22,
        )

        form_layout.setSpacing(
            12
        )

        form_title = QLabel(
            "IDENTITY DATA"
        )

        form_title.setObjectName(
            "cardTitle"
        )

        form_layout.addWidget(
            form_title
        )

        self.register_code = self._create_field(
            form_layout,
            "USER CODE",
            "Automatically generated",
        )

        self.register_code.setReadOnly(True)
        self.register_code.setText(
            self._generate_user_code()
        )

        self.register_first_name = (
            self._create_field(
                form_layout,
                "FIRST NAME",
                "First name",
            )
        )

        self.register_last_name = (
            self._create_field(
                form_layout,
                "LAST NAME",
                "Last name",
            )
        )

        self.register_email = (
            self._create_field(
                form_layout,
                "EMAIL",
                "Email address",
            )
        )

        self.register_phone = (
            self._create_field(
                form_layout,
                "PHONE",
                "Phone number",
            )
        )

        # -------------------------------------------------
        # Enrollment progress.
        # -------------------------------------------------

        progress_label = QLabel(
            "BIOMETRIC CAPTURE"
        )

        progress_label.setObjectName(
            "fieldLabel"
        )

        form_layout.addWidget(
            progress_label
        )

        self.enrollment_progress = (
            QProgressBar()
        )

        self.enrollment_progress.setObjectName(
            "enrollmentProgress"
        )

        self.enrollment_progress.setRange(
            0,
            self.face_auth_service.ENROLLMENT_SAMPLES,
        )

        self.enrollment_progress.setValue(
            0
        )

        self.enrollment_progress.setTextVisible(
            True
        )

        form_layout.addWidget(
            self.enrollment_progress
        )

        self.enrollment_status = QLabel(
            "Ready for enrollment."
        )

        self.enrollment_status.setObjectName(
            "formStatus"
        )

        self.enrollment_status.setWordWrap(
            True
        )

        form_layout.addWidget(
            self.enrollment_status
        )

        form_layout.addStretch()

        self.enroll_button = QPushButton(
            "START BIOMETRIC ENROLLMENT"
        )

        self.enroll_button.setObjectName(
            "primaryButton"
        )

        self.enroll_button.setMinimumHeight(
            46
        )

        self.enroll_button.clicked.connect(
            self._start_enrollment
        )

        form_layout.addWidget(
            self.enroll_button
        )

        reset_button = QPushButton(
            "RESET FORM"
        )

        reset_button.setObjectName(
            "secondaryButton"
        )

        reset_button.clicked.connect(
            self._reset_registration_form
        )

        form_layout.addWidget(
            reset_button
        )

        content.addWidget(
            form_card,
            stretch=1,
        )

        layout.addLayout(
            content,
            stretch=1,
        )

        return page

    def _create_field(
        self,
        layout: QVBoxLayout,
        label_text: str,
        placeholder: str,
    ) -> QLineEdit:
        """Create a form field."""

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "fieldLabel"
        )

        field = QLineEdit()

        field.setPlaceholderText(
            placeholder
        )

        field.setMinimumHeight(
            40
        )

        layout.addWidget(
            label
        )

        layout.addWidget(
            field
        )

        return field

    def _start_enrollment(self) -> None:
        """Begin collecting biometric samples."""

        if self._enrollment_active:
            return

        user_code = (
            self.register_code.text().strip()
        )

        first_name = (
            self.register_first_name.text().strip()
        )

        if not user_code:
            self._show_warning(
                "User code is required."
            )
            return

        if not first_name:
            self._show_warning(
                "First name is required."
            )
            return

        self._enrollment_frames = []

        self._enrollment_active = True

        self._last_enrollment_capture = 0.0

        self.enrollment_progress.setValue(
            0
        )

        self.enrollment_status.setText(
            "Look directly at the camera. "
            "Keep your face inside the frame."
        )

        self.enroll_button.setText(
            "CAPTURING BIOMETRIC SAMPLES..."
        )

        self.enroll_button.setEnabled(
            False
        )

        self.register_camera.start_camera()

    def _on_registration_frame(
        self,
        frame,
    ) -> None:
        """Collect enrollment samples from camera."""

        if not self._enrollment_active:
            return

        detections = (
            self.register_camera.get_latest_detections()
        )

        # We need exactly one face.
        if len(detections) != 1:
            self.enrollment_status.setText(
                "Exactly one face must be visible."
            )
            return

        now = time.monotonic()

        # Prevent collecting almost identical consecutive frames.
        if (
            now - self._last_enrollment_capture
            < 0.30
        ):
            return

        self._last_enrollment_capture = now

        self._enrollment_frames.append(
            frame
        )

        count = len(
            self._enrollment_frames
        )

        target = (
            self.face_auth_service.ENROLLMENT_SAMPLES
        )

        self.enrollment_progress.setValue(
            min(count, target)
        )

        self.enrollment_status.setText(
            f"Capturing biometric sample "
            f"{count}/{target}..."
        )

        if count >= target:
            self._finish_enrollment()

    def _finish_enrollment(self) -> None:
        """Build and store the biometric profile."""

        self._enrollment_active = False

        self.enroll_button.setText(
            "PROCESSING BIOMETRIC PROFILE..."
        )

        try:
            user = UserCreate(
                user_code=(
                    self.register_code
                    .text()
                    .strip()
                ),
                first_name=(
                    self.register_first_name
                    .text()
                    .strip()
                ),
                last_name=(
                    self.register_last_name
                    .text()
                    .strip()
                ),
                email=(
                    self.register_email
                    .text()
                    .strip()
                ),
                phone=(
                    self.register_phone
                    .text()
                    .strip()
                ),
            )

            created_user = (
                self.face_auth_service.register_from_samples(
                    user,
                    self._enrollment_frames,
                )
            )

            self.enrollment_status.setText(
                "BIOMETRIC PROFILE CREATED."
            )

            self.enrollment_progress.setValue(
                self.face_auth_service.ENROLLMENT_SAMPLES
            )

            self._refresh_users()
            self._refresh_dashboard()

            QMessageBox.information(
                self,
                "Enrollment Complete",
                (
                    f"Identity registered successfully.\n\n"
                    f"Name: "
                    f"{created_user.first_name} "
                    f"{created_user.last_name}\n"
                    f"Code: "
                    f"{created_user.user_code}"
                ),
            )

            self._reset_registration_form()

        except Exception as exc:
            self.enrollment_status.setText(
                f"Enrollment failed: {exc}"
            )

            QMessageBox.critical(
                self,
                "Enrollment Failed",
                str(exc),
            )

        finally:
            self.enroll_button.setEnabled(
                True
            )

            self.enroll_button.setText(
                "START BIOMETRIC ENROLLMENT"
            )

            self.register_camera.stop_camera()

            self._enrollment_frames = []

    def _reset_registration_form(self) -> None:
        """Reset registration UI."""

        self._enrollment_active = False
        self._enrollment_frames = []

        self.register_code.setText(
            self._generate_user_code()
        )
        self.register_first_name.clear()
        self.register_last_name.clear()
        self.register_email.clear()
        self.register_phone.clear()

        self.enrollment_progress.setValue(
            0
        )

        self.enrollment_status.setText(
            "Ready for enrollment."
        )

        self.enroll_button.setEnabled(
            True
        )

        self.enroll_button.setText(
            "START BIOMETRIC ENROLLMENT"
        )

        self.register_camera.stop_camera()

    # =====================================================
    # Authentication
    # =====================================================
    def _create_authenticate_page(self) -> QWidget:
        """Create the biometric authentication page."""
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(16)

        layout.addLayout(self._create_page_header(
            "IDENTITY AUTHENTICATION",
            "Real-time biometric verification",
        ))

        content = QHBoxLayout()
        content.setSpacing(18)

        # Camera
        camera_card = QFrame()
        camera_card.setObjectName("contentCard")

        camera_layout = QVBoxLayout(camera_card)
        camera_layout.setContentsMargins(12, 12, 12, 12)
        camera_layout.setSpacing(8)

        camera_title = QLabel("LIVE BIOMETRIC SENSOR")
        camera_title.setObjectName("cardTitle")

        camera_status = QLabel("CAMERA FEED")
        camera_status.setObjectName("cardText")

        camera_layout.addWidget(camera_title)
        camera_layout.addWidget(camera_status)

        self.authenticate_camera = CameraWidget(
            face_engine=self.face_engine
        )

        self.authenticate_camera.frame_captured.connect(
            self._process_authentication_frame
        )

        camera_layout.addWidget(
            self.authenticate_camera,
            stretch=1,
        )

        content.addWidget(camera_card, stretch=2)

        # Authentication panel
        panel = QFrame()
        panel.setObjectName("contentCard")
        panel.setMinimumWidth(340)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(24, 22, 24, 22)
        panel_layout.setSpacing(10)

        title = QLabel("AUTHENTICATION CORE")
        title.setObjectName("cardTitle")

        panel_layout.addWidget(title)

        description = QLabel(
            "Biometric verification status and identity result."
        )
        description.setObjectName("cardText")
        description.setWordWrap(True)

        panel_layout.addWidget(description)

        # Status
        status_label = QLabel("VERIFICATION STATUS")
        status_label.setObjectName("fieldLabel")

        panel_layout.addWidget(status_label)

        self.auth_indicator = QLabel("●  WAITING FOR FACE")
        self.auth_indicator.setObjectName("authIndicator")

        panel_layout.addWidget(self.auth_indicator)

        # Similarity
        score_label = QLabel("SIMILARITY SCORE")
        score_label.setObjectName("fieldLabel")

        panel_layout.addWidget(score_label)

        self.auth_score = QLabel("0.000")
        self.auth_score.setObjectName("authScore")
        self.auth_score.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        panel_layout.addWidget(self.auth_score)

        threshold_label = QLabel(
            f"Required threshold: {settings.face_match_threshold:.3f}"
        )
        threshold_label.setObjectName("cardText")

        panel_layout.addWidget(threshold_label)

        # Identity
        identity_label = QLabel("IDENTIFIED USER")
        identity_label.setObjectName("fieldLabel")

        panel_layout.addWidget(identity_label)

        self.auth_user = QLabel("NO IDENTITY MATCHED")
        self.auth_user.setObjectName("authUserUnknown")
        self.auth_user.setWordWrap(True)

        panel_layout.addWidget(self.auth_user)

        # Result
        result_card = QFrame()
        result_card.setObjectName("innerCard")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(14, 12, 14, 12)
        result_layout.setSpacing(4)

        result_title = QLabel("AUTHENTICATION RESULT")
        result_title.setObjectName("fieldLabel")

        self.auth_status = QLabel(
            "Authentication system ready."
        )
        self.auth_status.setObjectName("formStatus")
        self.auth_status.setWordWrap(True)

        result_layout.addWidget(result_title)
        result_layout.addWidget(self.auth_status)

        panel_layout.addWidget(result_card)

        # Instructions
        instruction_title = QLabel("VERIFICATION GUIDANCE")
        instruction_title.setObjectName("fieldLabel")

        panel_layout.addWidget(instruction_title)

        info = QLabel(
            "Position one face inside the camera frame. "
            "Keep your face clearly visible and look toward "
            "the camera during verification."
        )
        info.setObjectName("cardText")
        info.setWordWrap(True)

        panel_layout.addWidget(info)

        panel_layout.addStretch()

        # Runtime state
        runtime_card = QFrame()
        runtime_card.setObjectName("innerCard")

        runtime_layout = QHBoxLayout(runtime_card)
        runtime_layout.setContentsMargins(12, 9, 12, 9)

        runtime_label = QLabel("ENGINE")
        runtime_label.setObjectName("fieldLabel")

        runtime_value = QLabel("● READY")
        runtime_value.setObjectName("statusOnline")

        runtime_layout.addWidget(runtime_label)
        runtime_layout.addWidget(runtime_value)
        runtime_layout.addStretch()

        panel_layout.addWidget(runtime_card)

        content.addWidget(panel, stretch=1)

        layout.addLayout(content, stretch=1)

        return page
    
    def _process_authentication_frame(
        self,
        frame,
    ) -> None:
        """Run authentication periodically."""

        # Don't run recognition on every camera frame.
        now = time.monotonic()

        if not hasattr(
            self,
            "_last_authentication_time",
        ):
            self._last_authentication_time = 0.0

        if (
            now - self._last_authentication_time
            < 0.8
        ):
            return

        self._last_authentication_time = now

        detections = (
            self.authenticate_camera
            .get_latest_detections()
        )

        if len(detections) != 1:
            self.auth_indicator.setText(
                "● WAITING FOR FACE"
            )

            self.auth_user.setText(
                "NO IDENTITY MATCHED"
            )

            self.auth_score.setText(
                "0.000"
            )

            return

        try:
            result = (
                self.face_auth_service.authenticate(
                    frame,
                    detection=detections[0],
                )
            )

            self.auth_score.setText(
                f"{result.similarity_score:.3f}"
            )

            if result.authenticated:
                self.auth_indicator.setText(
                    "● IDENTITY VERIFIED"
                )

                if result.user is not None:
                    full_name = (
                        f"{result.user.first_name} "
                        f"{result.user.last_name}"
                    ).strip()

                    self.auth_user.setText(full_name.upper())
                    self.auth_user.setObjectName("authUserVerified")
                    self.auth_user.style().unpolish(self.auth_user)
                    self.auth_user.style().polish(self.auth_user)

                self.auth_status.setText(
                    result.message
                )

            else:
                self.auth_indicator.setText(
                    "● ACCESS NOT VERIFIED"
                )

                self.auth_user.setText("UNKNOWN IDENTITY")
                self.auth_user.setObjectName("authUserUnknown")
                self.auth_user.style().unpolish(self.auth_user)
                self.auth_user.style().polish(self.auth_user)

                self.auth_status.setText(
                    result.message
                )

        except Exception as exc:
            self.auth_status.setText(
                f"Authentication error: {exc}"
            )

    # =====================================================
    # Users
    # =====================================================

    def _create_users_page(self) -> QWidget:
        """Create the users management interface."""

        page = QWidget()
        page.setObjectName("usersPage")

        self.users_main_frame = QFrame()
        self.users_main_frame.setObjectName("usersMainFrame")

        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.users_main_frame)

        self.users_content_layout = QVBoxLayout(
            self.users_main_frame
        )

        self.users_content_layout.setContentsMargins(
            38,
            30,
            38,
            30,
        )

        self.users_content_layout.setSpacing(16)

        # -------------------------------------------------
        # Page Header
        # -------------------------------------------------

        self.users_content_layout.addLayout(
            self._create_page_header(
                "IDENTITY DATABASE",
                "Registered biometric identities",
            )
        )

        # -------------------------------------------------
        # Toolbar
        # -------------------------------------------------

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(10)

        self.user_search = QLineEdit()
        self.user_search.setObjectName("userSearch")
        self.user_search.setPlaceholderText(
            "Search identity, code, email or phone..."
        )
        self.user_search.setMinimumHeight(42)

        self.user_search.textChanged.connect(
            self._refresh_users
        )

        toolbar.addWidget(
            self.user_search,
            stretch=1,
        )

        refresh_button = QPushButton("↻  REFRESH")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.setMinimumHeight(42)

        refresh_button.clicked.connect(
            self._refresh_users
        )

        toolbar.addWidget(refresh_button)

        add_button = QPushButton("＋  NEW IDENTITY")
        add_button.setObjectName("primaryButton")
        add_button.setMinimumHeight(42)

        add_button.clicked.connect(
            lambda: self._show_page("Register User")
        )

        toolbar.addWidget(add_button)

        self.users_content_layout.addLayout(toolbar)

        # -------------------------------------------------
        # Users Table
        # -------------------------------------------------

        self.users_table = QTableWidget()
        self.users_table.setObjectName("usersTable")

        self.users_table.setColumnCount(5)

        self.users_table.setHorizontalHeaderLabels(
            [
                "CODE",
                "IDENTITY",
                "STATUS",
                "LAST AUTH",
                "ACTIONS",
            ]
        )

        # -------------------------------------------------
        # Table Behaviour
        # -------------------------------------------------

        self.users_table.cellDoubleClicked.connect(
            self._on_user_row_double_clicked
        )

        self.users_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.users_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.users_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.users_table.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        self.users_table.verticalHeader().setVisible(
            False
        )

        self.users_table.setAlternatingRowColors(True)
        self.users_table.setMouseTracking(True)
        self.users_table.viewport().setMouseTracking(True)

        # -------------------------------------------------
        # Table Header / Columns
        # -------------------------------------------------

        header = self.users_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Fixed,
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Fixed,
        )

        # Column widths
        self.users_table.setColumnWidth(0, 100)
        self.users_table.setColumnWidth(2, 110)
        self.users_table.setColumnWidth(3, 180)

        # Enough space for 3 action buttons
        self.users_table.setColumnWidth(4, 250)

        # -------------------------------------------------
        # Header Alignment
        # -------------------------------------------------

        for column in range(
            self.users_table.columnCount()
        ):
            header_item = (
                self.users_table.horizontalHeaderItem(
                    column
                )
            )

            if header_item is not None:
                header_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

        # -------------------------------------------------
        # Table
        # -------------------------------------------------

        self.users_content_layout.addWidget(
            self.users_table,
            stretch=1,
        )

        # -------------------------------------------------
        # Footer
        # -------------------------------------------------

        self.users_count = QLabel(
            "0 identities"
        )

        self.users_count.setObjectName(
            "tableFooter"
        )

        self.users_content_layout.addWidget(
            self.users_count
        )

        # -------------------------------------------------
        # User Detail
        # -------------------------------------------------

        self.user_detail_frame = (
            self._create_user_detail_frame()
        )

        # -------------------------------------------------
        # User Edit
        # -------------------------------------------------

        self.user_edit_frame = (
            self._create_user_edit_frame()
        )

        self.users_content_layout.addWidget(
            self.user_detail_frame
        )

        self.users_content_layout.addWidget(
            self.user_edit_frame
        )

        self.user_detail_frame.hide()
        self.user_edit_frame.hide()

        self._selected_user_id = None

        # -------------------------------------------------
        # Initial Load
        # -------------------------------------------------

        self._refresh_users()

        return page


    def _on_user_row_double_clicked(
        self,
        row: int,
        column: int,
    ) -> None:
        """Open user details when a table row is double-clicked."""

        item = self.users_table.item(
            row,
            0,
        )

        if item is None:
            return

        user_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if user_id is None:
            return

        self._show_user_detail(
            int(user_id)
        )


    # =====================================================
    # User Table
    # =====================================================

    def _refresh_users(self) -> None:
        """Refresh the users table."""

        if not hasattr(
            self,
            "users_table",
        ):
            return

        search = (
            self.user_search.text()
            if hasattr(
                self,
                "user_search",
            )
            else ""
        )

        try:
            users = self.face_auth_service.list_users(
                search=search
            )

        except Exception as exc:

            self.users_table.setRowCount(0)

            self.users_count.setText(
                f"Unable to load users: {exc}"
            )

            return

        # Clear table
        self.users_table.setRowCount(0)

        # -------------------------------------------------
        # Populate Users
        # -------------------------------------------------

        for row_index, user in enumerate(users):

            self.users_table.insertRow(
                row_index
            )

            # IMPORTANT:
            # Give the row enough vertical space for
            # the action buttons without changing
            # the button size.
            self.users_table.setRowHeight(
                row_index,
                44,
            )

            # -------------------------------------------------
            # User Data
            # -------------------------------------------------

            full_name = (
                f"{user.first_name} "
                f"{user.last_name}"
            ).strip()

            last_auth = (
                user.last_authenticated_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if user.last_authenticated_at
                else "NEVER"
            )

            values = [
                user.user_code,
                full_name,
                (
                    "ACTIVE"
                    if user.is_active
                    else "INACTIVE"
                ),
                last_auth,
            ]

            # -------------------------------------------------
            # Normal Cells
            # -------------------------------------------------

            for column_index, value in enumerate(values):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    user.id,
                )

                # Identity = left aligned
                if column_index == 1:

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter
                        | Qt.AlignmentFlag.AlignLeft
                    )

                # Everything else = centered
                else:

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.users_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

            # -------------------------------------------------
            # ACTIONS
            # -------------------------------------------------

            actions_widget = QWidget()

            actions_widget.setObjectName(
                "tableActionsWidget"
            )

            # ZERO margins.
            # The table controls the cell geometry.
            actions_layout = QHBoxLayout(
                actions_widget
            )

            actions_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            actions_layout.setSpacing(6)

            actions_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            # -------------------------------------------------
            # VIEW
            # -------------------------------------------------

            view_button = QPushButton(
                "VIEW"
            )

            view_button.setObjectName(
                "tableActionButton"
            )

            view_button.setProperty(
                "actionType",
                "view",
            )

            view_button.setFixedSize(
                52,
                26,
            )

            view_button.setToolTip(
                "View identity details"
            )

            view_button.clicked.connect(
                lambda checked=False,
                user_id=user.id:
                self._show_user_detail(
                    user_id
                )
            )

            # -------------------------------------------------
            # EDIT
            # -------------------------------------------------

            edit_button = QPushButton(
                "EDIT"
            )

            edit_button.setObjectName(
                "tableActionButton"
            )

            edit_button.setProperty(
                "actionType",
                "edit",
            )

            edit_button.setFixedSize(
                52,
                26,
            )

            edit_button.setToolTip(
                "Edit identity"
            )

            edit_button.clicked.connect(
                lambda checked=False,
                user_id=user.id:
                self._show_user_edit(
                    user_id
                )
            )

            # -------------------------------------------------
            # DELETE
            # -------------------------------------------------

            delete_button = QPushButton(
                "DELETE"
            )

            delete_button.setObjectName(
                "tableActionButton"
            )

            delete_button.setProperty(
                "actionType",
                "delete",
            )

            delete_button.setFixedSize(
                60,
                26,
            )

            delete_button.setToolTip(
                "Delete identity"
            )

            delete_button.clicked.connect(
                lambda checked=False,
                user_id=user.id:
                self._delete_user(
                    user_id
                )
            )

            # -------------------------------------------------
            # Add Buttons
            # -------------------------------------------------

            actions_layout.addWidget(
                view_button
            )

            actions_layout.addWidget(
                edit_button
            )

            actions_layout.addWidget(
                delete_button
            )

            # -------------------------------------------------
            # Put Action Widget Into Cell
            # -------------------------------------------------

            self.users_table.setCellWidget(
                row_index,
                4,
                actions_widget,
            )

        # -------------------------------------------------
        # Footer Count
        # -------------------------------------------------

        count = len(users)

        self.users_count.setText(
            f"{count} "
            + (
                "identity"
                if count == 1
                else "identities"
            )
        )
    # =====================================================
    # User detail frame
    # =====================================================

    def _create_user_detail_frame(self) -> QFrame:
        """Create the internal user detail frame."""

        frame = QFrame()
        frame.setObjectName(
            "userDetailFrame"
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        layout.setSpacing(18)

        # Header.

        header = QHBoxLayout()

        back_button = QPushButton(
            "←  BACK TO IDENTITIES"
        )

        back_button.setObjectName(
            "secondaryButton"
        )

        back_button.clicked.connect(
            self._hide_user_detail
        )

        header.addWidget(
            back_button
        )

        header.addStretch()

        self.user_detail_status = QLabel(
            "● ACTIVE"
        )

        self.user_detail_status.setObjectName(
            "userDetailStatus"
        )

        header.addWidget(
            self.user_detail_status
        )

        layout.addLayout(header)

        # Title.

        self.user_detail_title = QLabel(
            "IDENTITY PROFILE"
        )

        self.user_detail_title.setObjectName(
            "userDetailTitle"
        )

        layout.addWidget(
            self.user_detail_title
        )

        self.user_detail_subtitle = QLabel(
            "Biometric identity information"
        )

        self.user_detail_subtitle.setObjectName(
            "userDetailSubtitle"
        )

        layout.addWidget(
            self.user_detail_subtitle
        )

        # Information grid.

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(14)

        self.detail_code = self._create_detail_value(
            grid,
            0,
            0,
            "USER CODE",
        )

        self.detail_identity = self._create_detail_value(
            grid,
            0,
            1,
            "IDENTITY",
        )

        self.detail_email = self._create_detail_value(
            grid,
            1,
            0,
            "EMAIL",
        )

        self.detail_phone = self._create_detail_value(
            grid,
            1,
            1,
            "PHONE",
        )

        self.detail_registered = self._create_detail_value(
            grid,
            2,
            0,
            "REGISTERED",
        )

        self.detail_last_auth = self._create_detail_value(
            grid,
            2,
            1,
            "LAST AUTHENTICATION",
        )

        self.detail_embedding = self._create_detail_value(
            grid,
            3,
            0,
            "BIOMETRIC PROFILE",
        )

        self.detail_id = self._create_detail_value(
            grid,
            3,
            1,
            "DATABASE ID",
        )

        layout.addLayout(grid)

        # Actions.

        actions = QHBoxLayout()

        actions.addStretch()

        edit_button = QPushButton(
            "EDIT IDENTITY"
        )

        edit_button.setObjectName(
            "primaryButton"
        )

        edit_button.clicked.connect(
            self._edit_selected_user
        )

        actions.addWidget(
            edit_button
        )

        delete_button = QPushButton(
            "DELETE IDENTITY"
        )

        delete_button.setObjectName(
            "dangerButton"
        )

        delete_button.clicked.connect(
            self._delete_selected_user
        )

        actions.addWidget(
            delete_button
        )

        layout.addLayout(actions)

        return frame

    def _create_detail_value(
        self,
        grid: QGridLayout,
        row: int,
        column: int,
        title: str,
    ) -> QLabel:
        """Create a user detail information block."""

        container = QFrame()
        container.setObjectName(
            "userDetailItem"
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            14,
            10,
            14,
            10,
        )

        layout.setSpacing(3)

        title_label = QLabel(title)

        title_label.setObjectName(
            "userDetailLabel"
        )

        value_label = QLabel("—")

        value_label.setObjectName(
            "userDetailValue"
        )

        value_label.setWordWrap(True)

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        grid.addWidget(
            container,
            row,
            column,
        )

        return value_label

    # =====================================================
    # Show user detail
    # =====================================================

    def _show_user_detail(
        self,
        user_id: int,
    ) -> None:
        """Show a complete user detail frame."""

        try:
            user = self.face_auth_service.get_user(
                int(user_id)
            )

        except Exception as exc:
            self._show_error(
                "Unable to load user",
                str(exc),
            )
            return

        if user is None:
            self._show_error(
                "User not found",
                "The selected identity could not be loaded.",
            )
            return

        full_name = (
            f"{user.first_name} "
            f"{user.last_name}"
        ).strip()

        created = (
            user.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if user.created_at
            else "-"
        )

        last_auth = (
            user.last_authenticated_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if user.last_authenticated_at
            else "NEVER"
        )

        self._selected_user_id = user.id

        self.user_detail_title.setText(
            full_name.upper()
        )

        self.user_detail_subtitle.setText(
            f"IDENTITY / {user.user_code}"
        )

        self.user_detail_status.setText(
            "● ACTIVE"
            if user.is_active
            else "● INACTIVE"
        )

        self.detail_code.setText(
            user.user_code
        )

        self.detail_identity.setText(
            full_name
        )

        self.detail_email.setText(
            user.email or "Not provided"
        )

        self.detail_phone.setText(
            user.phone or "Not provided"
        )

        self.detail_registered.setText(
            created
        )

        self.detail_last_auth.setText(
            last_auth
        )

        self.detail_embedding.setText(
            f"ENABLED  /  "
            f"{user.embedding_dimension} dimensions"
        )

        self.detail_id.setText(
            str(user.id)
        )

        self.users_table.hide()
        self.user_search.hide()

        self.user_detail_frame.show()

    def _hide_user_detail(self) -> None:
        """Return from detail frame to users table."""

        self.user_detail_frame.hide()

        self.users_table.show()
        self.user_search.show()

        self._selected_user_id = None

    # =====================================================
    # User edit frame
    # =====================================================

    def _create_user_edit_frame(self) -> QFrame:
        """Create the internal user edit form."""

        frame = QFrame()

        frame.setObjectName(
            "userEditFrame"
        )

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        layout.setSpacing(16)

        header = QHBoxLayout()

        back_button = QPushButton(
            "←  CANCEL"
        )

        back_button.setObjectName(
            "secondaryButton"
        )

        back_button.clicked.connect(
            self._hide_user_edit
        )

        header.addWidget(
            back_button
        )

        header.addStretch()

        title = QLabel(
            "EDIT IDENTITY"
        )

        title.setObjectName(
            "userEditTitle"
        )

        header.addWidget(title)

        header.addStretch()

        layout.addLayout(header)

        form = QGridLayout()

        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.edit_user_code = self._create_edit_field(
            form,
            0,
            0,
            "USER CODE",
        )

        self.edit_first_name = self._create_edit_field(
            form,
            0,
            1,
            "FIRST NAME",
        )

        self.edit_last_name = self._create_edit_field(
            form,
            1,
            0,
            "LAST NAME",
        )

        self.edit_email = self._create_edit_field(
            form,
            1,
            1,
            "EMAIL",
        )

        self.edit_phone = self._create_edit_field(
            form,
            2,
            0,
            "PHONE",
        )

        layout.addLayout(form)

        actions = QHBoxLayout()

        actions.addStretch()

        cancel_button = QPushButton(
            "CANCEL"
        )

        cancel_button.setObjectName(
            "secondaryButton"
        )

        cancel_button.clicked.connect(
            self._hide_user_edit
        )

        actions.addWidget(
            cancel_button
        )

        save_button = QPushButton(
            "SAVE CHANGES"
        )

        save_button.setObjectName(
            "primaryButton"
        )

        save_button.clicked.connect(
            self._save_user_changes
        )

        actions.addWidget(
            save_button
        )

        layout.addLayout(actions)

        return frame

    def _create_edit_field(
        self,
        form: QGridLayout,
        row: int,
        column: int,
        label_text: str,
    ) -> QLineEdit:
        """Create an editable user field."""

        container = QFrame()
        container.setObjectName(
            "userEditField"
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(5)

        label = QLabel(label_text)

        label.setObjectName(
            "userEditLabel"
        )

        field = QLineEdit()

        field.setMinimumHeight(42)

        layout.addWidget(label)
        layout.addWidget(field)

        form.addWidget(
            container,
            row,
            column,
        )

        return field

    # =====================================================
    # Show edit
    # =====================================================

    def _show_user_edit(
        self,
        user_id: int,
    ) -> None:
        """Open user edit form."""

        try:
            user = self.face_auth_service.get_user(
                int(user_id)
            )

        except Exception as exc:
            self._show_error(
                "Unable to load user",
                str(exc),
            )
            return

        if user is None:
            self._show_error(
                "User not found",
                "The selected identity could not be loaded.",
            )
            return

        self._selected_user_id = user.id

        self.edit_user_code.setText(
            user.user_code
        )

        self.edit_first_name.setText(
            user.first_name
        )

        self.edit_last_name.setText(
            user.last_name
        )

        self.edit_email.setText(
            user.email
        )

        self.edit_phone.setText(
            user.phone
        )

        self.users_table.hide()
        self.user_search.hide()
        self.user_detail_frame.hide()

        self.user_edit_frame.show()

    def _edit_selected_user(self) -> None:
        """Edit the currently displayed user."""

        if self._selected_user_id is None:
            return

        self._show_user_edit(
            self._selected_user_id
        )

    def _hide_user_edit(self) -> None:
        """Close user edit form."""

        self.user_edit_frame.hide()

        self.users_table.show()
        self.user_search.show()

        self._selected_user_id = None

    # =====================================================
    # Save user
    # =====================================================

    def _save_user_changes(self) -> None:
        """Save edited user information."""

        if self._selected_user_id is None:
            return

        user_code = (
            self.edit_user_code.text().strip()
        )

        first_name = (
            self.edit_first_name.text().strip()
        )

        last_name = (
            self.edit_last_name.text().strip()
        )

        email = (
            self.edit_email.text().strip()
        )

        phone = (
            self.edit_phone.text().strip()
        )

        if not user_code:
            self._show_error(
                "Invalid user code",
                "User code cannot be empty.",
            )
            return

        if not first_name:
            self._show_error(
                "Invalid first name",
                "First name cannot be empty.",
            )
            return

        try:
            self.face_auth_service.update_user(
                user_id=self._selected_user_id,
                user_code=user_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )

        except Exception as exc:
            self._show_error(
                "Unable to save changes",
                str(exc),
            )
            return

        self._hide_user_edit()
        self._refresh_users()

        self._show_success(
            "Identity updated",
            "User information has been updated successfully.",
        )

    # =====================================================
    # Delete
    # =====================================================

    def _delete_selected_user(self) -> None:
        """Delete currently selected user."""

        if self._selected_user_id is None:
            return

        self._delete_user(
            self._selected_user_id
        )

    def _delete_user(
        self,
        user_id: int,
    ) -> None:
        """Deactivate a user after confirmation."""

        try:
            user = self.face_auth_service.get_user(
                int(user_id)
            )

        except Exception as exc:
            self._show_error(
                "Unable to load user",
                str(exc),
            )
            return

        if user is None:
            self._show_error(
                "User not found",
                "The selected identity no longer exists.",
            )
            return

        full_name = (
            f"{user.first_name} "
            f"{user.last_name}"
        ).strip()

        confirmed = self._confirm_action(
            "DELETE IDENTITY",
            (
                f"Are you sure you want to deactivate "
                f"'{full_name}'?\n\n"
                "The biometric profile will no longer "
                "be available for authentication."
            ),
        )

        if not confirmed:
            return

        try:
            self.face_auth_service.deactivate_user(
                int(user_id)
            )

        except Exception as exc:
            self._show_error(
                "Unable to delete identity",
                str(exc),
            )
            return

        self._selected_user_id = None

        self.user_detail_frame.hide()
        self.user_edit_frame.hide()

        self.users_table.show()
        self.user_search.show()

        self._refresh_users()

        self._show_success(
            "Identity deactivated",
            f"{full_name} has been removed from active identities.",
        )

    # =====================================================
    # Settings
    # =====================================================

    def _create_settings_page(self) -> QWidget:
        """Create the system settings and information page."""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(18)

        # =================================================
        # Page Header
        # =================================================

        layout.addLayout(self._create_page_header(
            "SYSTEM CONFIGURATION",
            "Biometric engine and application configuration",
        ))

        # =================================================
        # Scroll Area
        # =================================================

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 10, 0)
        container_layout.setSpacing(14)

        # =================================================
        # RECOGNITION ENGINE
        # =================================================

        recognition_card = QFrame()
        recognition_card.setObjectName("contentCard")

        recognition_layout = QVBoxLayout(recognition_card)
        recognition_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("RECOGNITION ENGINE")
        title.setObjectName("cardTitle")
        recognition_layout.addWidget(title)

        threshold = QLabel("Face match threshold")
        threshold.setObjectName("fieldLabel")
        recognition_layout.addWidget(threshold)

        self.threshold_value = QLabel(f"{settings.face_match_threshold:.3f}")
        self.threshold_value.setObjectName("settingValue")
        recognition_layout.addWidget(self.threshold_value)

        model = QLabel("Recognition model")
        model.setObjectName("fieldLabel")
        recognition_layout.addWidget(model)

        model_value = QLabel("Face Recognition Engine")
        model_value.setObjectName("settingValue")
        recognition_layout.addWidget(model_value)

        distance = QLabel("Matching method")
        distance.setObjectName("fieldLabel")
        recognition_layout.addWidget(distance)

        distance_value = QLabel("Cosine similarity")
        distance_value.setObjectName("settingValue")
        recognition_layout.addWidget(distance_value)

        description = QLabel(
            "Higher threshold values make recognition stricter. "
            "The configured threshold is used by the authentication engine."
        )
        description.setObjectName("cardText")
        description.setWordWrap(True)
        recognition_layout.addWidget(description)

        container_layout.addWidget(recognition_card)

        # =================================================
        # VISION ENGINE
        # =================================================

        detection_card = QFrame()
        detection_card.setObjectName("contentCard")

        detection_layout = QVBoxLayout(detection_card)
        detection_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("VISION ENGINE")
        title.setObjectName("cardTitle")
        detection_layout.addWidget(title)

        scale_label = QLabel("Detection scale")
        scale_label.setObjectName("fieldLabel")
        detection_layout.addWidget(scale_label)

        scale_value = QLabel(f"{settings.face_detection_scale:.2f}")
        scale_value.setObjectName("settingValue")
        detection_layout.addWidget(scale_value)

        detector_label = QLabel("Face detector")
        detector_label.setObjectName("fieldLabel")
        detection_layout.addWidget(detector_label)

        detector_value = QLabel("YuNet")
        detector_value.setObjectName("settingValue")
        detection_layout.addWidget(detector_value)

        processing_label = QLabel("Processing mode")
        processing_label.setObjectName("fieldLabel")
        detection_layout.addWidget(processing_label)

        processing_value = QLabel("Real-time camera processing")
        processing_value.setObjectName("settingValue")
        detection_layout.addWidget(processing_value)

        info = QLabel(
            "YuNet performs face detection on a scaled "
            "camera frame to maintain real-time performance."
        )
        info.setObjectName("cardText")
        info.setWordWrap(True)
        detection_layout.addWidget(info)

        container_layout.addWidget(detection_card)

        # =================================================
        # DATABASE
        # =================================================

        database_card = QFrame()
        database_card.setObjectName("contentCard")

        database_layout = QVBoxLayout(database_card)
        database_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("DATABASE")
        title.setObjectName("cardTitle")
        database_layout.addWidget(title)

        database_info = QLabel("Database type")
        database_info.setObjectName("fieldLabel")
        database_layout.addWidget(database_info)

        database_value = QLabel("SQLite")
        database_value.setObjectName("settingValue")
        database_layout.addWidget(database_value)

        cache_label = QLabel("Embedding cache")
        cache_label.setObjectName("fieldLabel")
        database_layout.addWidget(cache_label)

        cache_value = QLabel("ACTIVE")
        cache_value.setObjectName("statusOnline")
        database_layout.addWidget(cache_value)

        profile_label = QLabel("Profile format")
        profile_label.setObjectName("fieldLabel")
        database_layout.addWidget(profile_label)

        profile_value = QLabel("float32 normalized vectors")
        profile_value.setObjectName("settingValue")
        database_layout.addWidget(profile_value)

        self.embedding_count_label = QLabel(
            f"Loaded profiles: {len(self.face_auth_service._embedding_cache)}"
        )
        self.embedding_count_label.setObjectName("diagnosticText")
        database_layout.addWidget(self.embedding_count_label)

        refresh_cache = QPushButton("↻  REFRESH EMBEDDING CACHE")
        refresh_cache.setObjectName("secondaryButton")
        refresh_cache.clicked.connect(self._refresh_embedding_cache)
        database_layout.addWidget(refresh_cache)

        container_layout.addWidget(database_card)

        # =================================================
        # SYSTEM STATUS
        # =================================================

        status_card = QFrame()
        status_card.setObjectName("contentCard")

        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("SYSTEM STATUS")
        title.setObjectName("cardTitle")
        status_layout.addWidget(title)

        app_label = QLabel("APPLICATION")
        app_label.setObjectName("fieldLabel")
        status_layout.addWidget(app_label)

        app_status = QLabel("●  ONLINE")
        app_status.setObjectName("statusOnline")
        status_layout.addWidget(app_status)

        engine_label = QLabel("AUTHENTICATION ENGINE")
        engine_label.setObjectName("fieldLabel")
        status_layout.addWidget(engine_label)

        engine_status = QLabel("●  READY")
        engine_status.setObjectName("statusOnline")
        status_layout.addWidget(engine_status)

        db_label = QLabel("DATABASE")
        db_label.setObjectName("fieldLabel")
        status_layout.addWidget(db_label)

        db_status = QLabel("●  CONNECTED")
        db_status.setObjectName("statusOnline")
        status_layout.addWidget(db_status)

        camera_label = QLabel("CAMERA")
        camera_label.setObjectName("fieldLabel")
        status_layout.addWidget(camera_label)

        camera_status = QLabel("●  MANAGED BY AUTHENTICATION MODULE")
        camera_status.setObjectName("statusInfo")
        status_layout.addWidget(camera_status)

        container_layout.addWidget(status_card)

        # =================================================
        # APPLICATION INFORMATION
        # =================================================

        application_card = QFrame()
        application_card.setObjectName("contentCard")

        application_layout = QVBoxLayout(application_card)
        application_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("APPLICATION INFORMATION")
        title.setObjectName("cardTitle")
        application_layout.addWidget(title)

        app_name = QLabel("Application")
        app_name.setObjectName("fieldLabel")
        application_layout.addWidget(app_name)

        app_name_value = QLabel("VIGIL FACE AUTHENTICATION")
        app_name_value.setObjectName("settingValue")
        application_layout.addWidget(app_name_value)

        version = QLabel("Version")
        version.setObjectName("fieldLabel")
        application_layout.addWidget(version)

        version_value = QLabel("1.0.0")
        version_value.setObjectName("settingValue")
        application_layout.addWidget(version_value)

        build = QLabel("Build")
        build.setObjectName("fieldLabel")
        application_layout.addWidget(build)

        build_value = QLabel("CORE SYSTEM")
        build_value.setObjectName("settingValue")
        application_layout.addWidget(build_value)

        environment = QLabel("Environment")
        environment.setObjectName("fieldLabel")
        application_layout.addWidget(environment)

        environment_value = QLabel("Desktop / Local")
        environment_value.setObjectName("settingValue")
        application_layout.addWidget(environment_value)

        container_layout.addWidget(application_card)

        # =================================================
        # DEVELOPER INFORMATION
        # =================================================

        developer_card = QFrame()
        developer_card.setObjectName("contentCard")

        developer_layout = QVBoxLayout(developer_card)
        developer_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("DEVELOPER INFORMATION")
        title.setObjectName("cardTitle")
        developer_layout.addWidget(title)

        developer = QLabel("Developer")
        developer.setObjectName("fieldLabel")
        developer_layout.addWidget(developer)

        developer_value = QLabel("Shreekanth Kapparagaon")
        developer_value.setObjectName("settingValue")
        developer_layout.addWidget(developer_value)

        project = QLabel("Project")
        project.setObjectName("fieldLabel")
        developer_layout.addWidget(project)

        project_value = QLabel("VIGIL FACE AUTHENTICATION System")
        project_value.setObjectName("settingValue")
        developer_layout.addWidget(project_value)

        technology = QLabel("Technology")
        technology.setObjectName("fieldLabel")
        developer_layout.addWidget(technology)

        technology_value = QLabel("Python • PySide6 • OpenCV • SQLite")
        technology_value.setObjectName("settingValue")
        developer_layout.addWidget(technology_value)

        architecture = QLabel("Architecture")
        architecture.setObjectName("fieldLabel")
        developer_layout.addWidget(architecture)

        architecture_value = QLabel("Desktop biometric authentication platform")
        architecture_value.setObjectName("settingValue")
        developer_layout.addWidget(architecture_value)

        developer_description = QLabel(
            "VIGIL is designed as a local biometric authentication "
            "system with real-time face detection, recognition and "
            "identity management."
        )
        developer_description.setObjectName("cardText")
        developer_description.setWordWrap(True)
        developer_layout.addWidget(developer_description)

        container_layout.addWidget(developer_card)

        # =================================================
        # MAINTENANCE
        # =================================================

        maintenance_card = QFrame()
        maintenance_card.setObjectName("contentCard")

        maintenance_layout = QVBoxLayout(maintenance_card)
        maintenance_layout.setContentsMargins(24, 22, 24, 22)

        title = QLabel("MAINTENANCE")
        title.setObjectName("cardTitle")
        maintenance_layout.addWidget(title)

        maintenance_info = QLabel(
            "Use these operations to refresh runtime resources "
            "without restarting the application."
        )
        maintenance_info.setObjectName("cardText")
        maintenance_info.setWordWrap(True)
        maintenance_layout.addWidget(maintenance_info)

        refresh_cache_button = QPushButton("↻  REFRESH EMBEDDING CACHE")
        refresh_cache_button.setObjectName("secondaryButton")
        refresh_cache_button.clicked.connect(self._refresh_embedding_cache)
        maintenance_layout.addWidget(refresh_cache_button)

        container_layout.addWidget(maintenance_card)
        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        return page

    def _refresh_embedding_cache(self) -> None:
        """Refresh in-memory embeddings."""

        try:
            self.face_auth_service.refresh_embedding_cache()
            count = len(self.face_auth_service._embedding_cache)

            if hasattr(self, "embedding_count_label"):
                self.embedding_count_label.setText(f"Loaded profiles: {count}")

            QMessageBox.information(
                self,
                "Cache Refreshed",
                f"Embedding cache refreshed successfully.\n\nLoaded profiles: {count}",
            )

        except Exception as exc:
            QMessageBox.critical(self, "Cache Error", str(exc))    
    
    def _refresh_dashboard(self) -> None:
        """Refresh dashboard runtime information."""
        try:
            users = self.face_auth_service.list_users()
            count = len(users)
            cache_count = len(self.face_auth_service._embedding_cache)

            self.dashboard_users_value.setText(str(count))
            self.dashboard_auth_value.setText("READY")
            self.dashboard_camera_value.setText("STANDBY")
            self.dashboard_security_value.setText("ACTIVE")

            values = {
                "Face detector": "ONLINE",
                "Recognition engine": "ONLINE",
                "Database": "CONNECTED",
                "Embedding cache": f"{cache_count} LOADED",
                "Authentication service": "READY",
                "Camera subsystem": "STANDBY",
            }

            for label, value in values.items():
                widget = self.dashboard_diagnostic_values.get(label)

                if widget:
                    widget.setText(f"●  {value}")

        except Exception as exc:
            self.dashboard_users_value.setText("ERROR")
            self.dashboard_auth_value.setText("UNAVAILABLE")

            for widget in self.dashboard_diagnostic_values.values():
                widget.setText("●  ERROR")

            QMessageBox.warning(
                self,
                "Dashboard Error",
                f"Unable to load system information.\n\n{exc}",
            )
    

    # =====================================================
    # User action messages
    # =====================================================

    def _show_error(
        self,
        title: str,
        message: str,
    ) -> None:
        """Show application error alert."""

        try:
            self._show_alert(
                title,
                message,
                "error",
            )
        except AttributeError:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                title,
                message,
            )

    def _show_success(
        self,
        title: str,
        message: str,
    ) -> None:
        """Show application success alert."""

        try:
            self._show_alert(
                title,
                message,
                "success",
            )
        except AttributeError:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                title,
                message,
            )

    def _confirm_action(
        self,
        title: str,
        message: str,
    ) -> bool:
        """Show confirmation message."""

        try:
            return bool(
                self._show_alert(
                    title,
                    message,
                    "warning",
                    confirm=True,
                )
            )

        except AttributeError:
            from PyQt6.QtWidgets import QMessageBox

            result = QMessageBox.question(
                self,
                title,
                message,
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
            )

            return (
                result
                == QMessageBox.StandardButton.Yes
            )


    # =====================================================
    # Navigation
    # =====================================================

    def _show_page(
        self,
        page_name: str,
    ) -> None:
        """Switch application page safely."""

        page_map = {
            "Dashboard": self.dashboard_page,
            "Register User": self.register_page,
            "Authenticate": self.authenticate_page,
            "Users": self.users_page,
            "Settings": self.settings_page,
        }

        page = page_map.get(
            page_name
        )

        if page is None:
            return

        # -------------------------------------------------
        # Stop cameras that are not needed.
        # -------------------------------------------------

        if page_name != "Authenticate":
            self.authenticate_camera.stop_camera()

        if page_name != "Register User":
            self.register_camera.stop_camera()

        # -------------------------------------------------
        # Change page.
        # -------------------------------------------------

        self.content_stack.setCurrentWidget(
            page
        )

        # -------------------------------------------------
        # Update sidebar.
        # -------------------------------------------------

        for name, button in (
            self._navigation_buttons.items()
        ):
            button.setProperty(
                "active",
                name == page_name,
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

        # -------------------------------------------------
        # Start required camera.
        # -------------------------------------------------

        if page_name == "Authenticate":
            self.authenticate_camera.start_camera()

        elif page_name == "Register User":
            # Registration camera remains off until
            # enrollment begins.
            pass

        # -------------------------------------------------
        # Refresh data.
        # -------------------------------------------------

        if page_name == "Dashboard":
            self._refresh_dashboard()

        elif page_name == "Users":
            self._refresh_users()

    # =====================================================
        # Footer
    # =====================================================

    def _create_application_footer(self) -> QWidget:
        footer = QFrame()
        footer.setObjectName("applicationFooter")
        footer.setFixedHeight(28)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(6)

        left = QLabel("♥  Built with curiosity & caffeine")
        left.setObjectName("footerLeft")

        center = QLabel("VIGIL FACE AUTHENTICATION")
        center.setObjectName("footerAccent")

        right = QLabel("v1.0.0  •  LOCAL")
        right.setObjectName("footerRight")

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(center)
        layout.addStretch()
        layout.addWidget(right)

        return footer
    
    
    # =====================================================
    # Utility
    # =====================================================
    @staticmethod
    def _show_warning(
        message: str,
    ) -> None:
        """Show warning dialog."""

        QMessageBox.warning(
            None,
            "Validation",
            message,
        )

    # =====================================================
    # Window lifecycle
    # =====================================================

    def closeEvent(
        self,
        event,
    ) -> None:
        """Shutdown camera resources safely."""

        self._enrollment_active = False

        self.authenticate_camera.stop_camera()
        self.register_camera.stop_camera()

        # Give workers a short opportunity to finish.
        deadline = time.monotonic() + 2.0

        while (
            time.monotonic() < deadline
            and (
                (
                    self.authenticate_camera.worker
                    is not None
                    and self.authenticate_camera.worker.isRunning()
                )
                or (
                    self.register_camera.worker
                    is not None
                    and self.register_camera.worker.isRunning()
                )
            )
        ):
            from PyQt6.QtWidgets import QApplication

            QApplication.processEvents()

            time.sleep(0.02)

        event.accept()

