from __future__ import annotations


APP_STYLE = """
#pageCode,
#diagnosticText,
#authScore,
#authUserVerified,
#authUserUnknown {
    font-family: "Cascadia Mono";
}

/* =========================================================
   FUTURISTIC FACE AUTHENTICATION UI
   ========================================================= */

QMainWindow,
QWidget {
    background-color: #070b12;
    color: #e8f7ff;
    font-family: "Segoe UI";
    font-size: 14px;
}

QLabel {
    color: #e8f7ff;
}

QPushButton {
    border: none;
    outline: none;
}


/* =========================================================
   MAIN WINDOW
   ========================================================= */

#mainCentralWidget,
#contentStack {
    background-color: #070b12;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

#sidebar {
    background-color: #080d15;
    border-right: 1px solid #15283a;
}

#brandTitle {
    color: #ffffff;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 2px;
}

#brandSubtitle {
    color: #4e8aa5;
    font-size: 11px;
    letter-spacing: 1px;
}

#sidebarButton {
    background-color: transparent;
    color: #6e8a9a;
    text-align: left;
    padding: 0 16px;
    border-radius: 8px;
    border-left: 2px solid transparent;
    font-size: 13px;
    font-weight: 600;
}

#sidebarButton:hover {
    background-color: #0c1924;
    color: #c9f5ff;
    border-left: 2px solid #00eaff;
}

#sidebarButton:pressed {
    background-color: #102330;
}

#sidebarButton[active="true"] {
    background-color: #0b202d;
    color: #00eaff;
    border-left: 2px solid #00eaff;
    font-weight: 700;
}

#sidebarVersion {
    color: #345263;
    font-size: 10px;
    letter-spacing: 0.5px;
}


/* =========================================================
   PAGE HEADERS
   ========================================================= */

#pageTitle {
    color: #f2fbff;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

#pageSubtitle {
    color: #577484;
    font-size: 13px;
}


/* =========================================================
   DASHBOARD
   ========================================================= */

#statCard {
    background-color: #0a111a;
    border: 1px solid #162b3a;
    border-radius: 12px;
}

#statCard:hover {
    border-color: #00aeca;
}

#statTitle {
    color: #557487;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

#statValue {
    color: #00eaff;
    font-size: 28px;
    font-weight: 800;
    padding-top: 4px;
}

#statDescription {
    color: #3e5b6c;
    font-size: 11px;
}

#contentCard {
    background-color: #0a111a;
    border: 1px solid #162b3a;
    border-radius: 12px;
}

#cardTitle {
    color: #dffaff;
    font-size: 16px;
    font-weight: 700;
}

#cardText {
    color: #638091;
    font-size: 13px;
}


/* =========================================================
   CAMERA
   ========================================================= */

#cameraFrame {
    background-color: #05090f;
    border: 1px solid #143246;
    border-radius: 14px;
}

#cameraPreview {
    background-color: #02050a;
    border: 1px solid #0c2a3b;
    border-radius: 10px;
    color: #294c5d;
    font-size: 13px;
}

#cameraStatus,
#cameraStatusActive {
    font-size: 11px;
    padding-left: 4px;
}

#cameraStatus {
    color: #557789;
}

#cameraStatusActive {
    color: #00ffb3;
}


/* =========================================================
   AUTHENTICATION STATUS
   ========================================================= */

#authenticationStatus {
    background-color: #08151d;
    border: 1px solid #124055;
    border-radius: 8px;
    color: #65a5ba;
    padding: 12px 16px;
    font-size: 12px;
}


/* =========================================================
   FORMS
   ========================================================= */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox {
    background-color: #09121b;
    color: #dffaff;
    border: 1px solid #173243;
    border-radius: 7px;
    padding: 9px 11px;
    selection-background-color: #006b82;
}

QLineEdit:hover,
QTextEdit:hover,
QPlainTextEdit:hover,
QComboBox:hover {
    border-color: #1d6178;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus {
    border-color: #00dffc;
    background-color: #0a1721;
}


/* =========================================================
   PRIMARY BUTTON
   ========================================================= */

QPushButton#primaryButton {
    background-color: #007f96;
    color: #ffffff;
    border: 1px solid #00dffc;
    border-radius: 7px;
    padding: 10px 18px;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #009db8;
    border-color: #5cffff;
}

QPushButton#primaryButton:pressed {
    background-color: #00687d;
}

QPushButton#primaryButton:disabled {
    background-color: #101b24;
    color: #3b5968;
    border-color: #1b303d;
}


/* =========================================================
   SECONDARY BUTTON
   ========================================================= */

QPushButton#secondaryButton {
    background-color: #0c151e;
    color: #91aebb;
    border: 1px solid #203846;
    border-radius: 7px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#secondaryButton:hover {
    background-color: #10212c;
    color: #d8faff;
    border-color: #34748a;
}

QPushButton#secondaryButton:pressed {
    background-color: #081119;
}


/* =========================================================
   TABLES
   ========================================================= */

QTableWidget,
QTableView {
    background-color: #080f17;
    alternate-background-color: #0b151f;
    color: #d8f7ff;
    border: 1px solid #173243;
    border-radius: 10px;
    gridline-color: #102634;
    selection-background-color: #073d4c;
    selection-color: #00f0ff;
}

QTableWidget::item,
QTableView::item {
    padding: 8px;
}

QTableWidget::item:selected,
QTableView::item:selected {
    background-color: #073d4c;
    color: #9cffff;
}

QHeaderView::section {
    background-color: #0b1721;
    color: #5e92a5;
    border: none;
    border-bottom: 1px solid #173243;
    padding: 10px;
    font-size: 11px;
    font-weight: 700;
}


/* =========================================================
   USERS TABLE
   ========================================================= */

#usersPage,
#usersMainFrame {
    background-color: #0b0f16;
}

QTableWidget#usersTable {
    background-color: #101620;
    color: #d8f7ff;
    border: 1px solid #263342;
    border-radius: 12px;
    gridline-color: #1d2936;
    selection-background-color: #123b4a;
    selection-color: #ffffff;
    font-size: 14px;
}

QTableWidget#usersTable::item {
    background-color: transparent;
    border: none;
    padding: 0px 12px;
}

QTableWidget#usersTable::item:selected {
    background-color: #123b4a;
    color: #ffffff;
}

QTableWidget#usersTable::item:hover {
    background-color: #111f2b;
}

QTableWidget#usersTable QHeaderView::section {
    font-size: 12px;
    padding: 12px 10px;
}

/* =====================================================
   TABLE ACTION BUTTONS
   ===================================================== */

QPushButton#tableActionButton {
    background-color: #111923;
    color: #dcecff;

    border: 1px solid #29445a;
    border-radius: 5px;

    padding: 0px;
    margin: 0px;

    font-family: "Segoe UI";
    font-size: 9px;
    font-weight: 700;
}

QPushButton#tableActionButton:hover {
    background-color: #182b3a;
    border-color: #00e5ff;
    color: #ffffff;
}

QPushButton#tableActionButton:pressed {
    background-color: #0d1c27;
    border-color: #00e5ff;
    color: #00e5ff;
}


/* -----------------------------------------------------
   VIEW
   ----------------------------------------------------- */

QPushButton#tableActionButton[actionType="view"] {
    color: #00e5ff;
    border-color: #24566b;
}

QPushButton#tableActionButton[actionType="view"]:hover {
    background-color: #102c38;
    border-color: #00e5ff;
    color: #ffffff;
}


/* -----------------------------------------------------
   EDIT
   ----------------------------------------------------- */

QPushButton#tableActionButton[actionType="edit"] {
    color: #9faeff;
    border-color: #39486e;
}

QPushButton#tableActionButton[actionType="edit"]:hover {
    background-color: #202846;
    border-color: #718cff;
    color: #ffffff;
}


/* -----------------------------------------------------
   DELETE
   ----------------------------------------------------- */

QPushButton#tableActionButton[actionType="delete"] {
    color: #ff7180;
    border-color: #69343d;
}

QPushButton#tableActionButton[actionType="delete"]:hover {
    background-color: #3a1d24;
    border-color: #ff5367;
    color: #ffffff;
}


/* =====================================================
   TABLE ACTION CONTAINER
   ===================================================== */

QWidget#tableActionsWidget {
    background-color: transparent;
    border: none;

    padding: 0px;
    margin: 0px;
}

/* =========================================================
   USER DETAIL
   ========================================================= */

#userDetailFrame {
    background-color: #101721;
    border: 1px solid #285064;
    border-radius: 14px;
}

#userDetailCard {
    background-color: #09121b;
    border: 1px solid #173243;
    border-radius: 12px;
}

#userDetailTitle {
    color: #e9fbff;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 1px;
}

#userDetailSubtitle {
    color: #617889;
    font-size: 12px;
    letter-spacing: 1px;
}

#userDetailStatus {
    color: #64f5b0;
    font-size: 12px;
    font-weight: 700;
    padding: 7px 12px;
    background-color: #10251e;
    border: 1px solid #235a43;
    border-radius: 6px;
}

#userDetailItem {
    background-color: #0c131c;
    border: 1px solid #1f2e3b;
    border-radius: 8px;
}

#userDetailLabel {
    color: #597082;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

#userDetailValue {
    color: #dcecf2;
    font-size: 14px;
    font-weight: 600;
}

#userDetailAccent {
    color: #00eaff;
}


/* =========================================================
   USER EDIT
   ========================================================= */

#userEditFrame {
    background-color: #101721;
    border: 1px solid #304b5c;
    border-radius: 14px;
}

#userEditTitle {
    color: #e9fbff;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}

#userEditField {
    background-color: transparent;
}

#userEditLabel {
    color: #668092;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

#userEditFrame QLineEdit {
    background-color: #0b121a;
    border: 1px solid #263846;
    border-radius: 7px;
    color: #dcecf2;
    padding: 9px 11px;
}

#userEditFrame QLineEdit:hover {
    border-color: #31576a;
}

#userEditFrame QLineEdit:focus {
    border-color: #39cbe8;
}


/* =========================================================
   DANGER BUTTON
   ========================================================= */

QPushButton#dangerButton {
    background-color: #34151c;
    color: #ff7185;
    border: 1px solid #71313e;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 700;
}

QPushButton#dangerButton:hover {
    background-color: #481b25;
    border-color: #a74355;
    color: #ff9aaa;
}

QPushButton#dangerButton:pressed {
    background-color: #281016;
}


/* =========================================================
   STATUS INDICATORS
   ========================================================= */

#statusOnline {
    color: #00ffb3;
    font-weight: 700;
}

#statusOffline {
    color: #ff365d;
    font-weight: 700;
}

#statusWarning {
    color: #ffd000;
    font-weight: 700;
}

#statusInfo {
    color: #00eaff;
    font-weight: 700;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

#neonDivider,
#neonDividerCyan,
#neonDividerGreen {
    min-height: 1px;
    max-height: 1px;
}

#neonDivider {
    background-color: #123040;
}

#neonDividerCyan {
    background-color: #00dffc;
}

#neonDividerGreen {
    background-color: #00ffb3;
}


/* =========================================================
   ALERT SYSTEM
   ========================================================= */

#alertDialog {
    background-color: #070d14;
    border: 1px solid #183443;
    border-radius: 14px;
}

#alertTitle {
    color: #f2fbff;
    font-size: 18px;
    font-weight: 800;
}

#alertMessage {
    color: #72909f;
    font-size: 13px;
}

#alertIcon {
    font-size: 30px;
    font-weight: 800;
}

#alertTypeLabel {
    color: #416a7a;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.2px;
}


/* INFO */

#alertDialog[alertType="info"] {
    border-color: #00dffc;
}

#alertDialog[alertType="info"] #alertIcon {
    color: #00eaff;
}

#alertDialog[alertType="info"] #alertTitle {
    color: #8df6ff;
}

#alertDialog[alertType="info"] #alertMessage {
    color: #6596a5;
}

#alertDialog[alertType="info"] #alertAccent,
#alertDialog[alertType="info"] #alertTypeLabel {
    color: #00cfe8;
    background-color: #00eaff;
}


/* SUCCESS */

#alertDialog[alertType="success"] {
    border-color: #00ffb3;
}

#alertDialog[alertType="success"] #alertIcon {
    color: #00ffb3;
}

#alertDialog[alertType="success"] #alertTitle {
    color: #78ffd0;
}

#alertDialog[alertType="success"] #alertMessage {
    color: #629d88;
}

#alertDialog[alertType="success"] #alertAccent {
    background-color: #00ffb3;
}

#alertDialog[alertType="success"] #alertTypeLabel {
    color: #00ffb3;
}


/* WARNING */

#alertDialog[alertType="warning"] {
    border-color: #ffd000;
}

#alertDialog[alertType="warning"] #alertIcon {
    color: #ffd000;
}

#alertDialog[alertType="warning"] #alertTitle {
    color: #ffe46b;
}

#alertDialog[alertType="warning"] #alertMessage {
    color: #a89451;
}

#alertDialog[alertType="warning"] #alertAccent,
#alertDialog[alertType="warning"] #alertTypeLabel {
    background-color: #ffd000;
}

#alertDialog[alertType="warning"] #alertTypeLabel {
    color: #ffd000;
}


/* ERROR */

#alertDialog[alertType="error"] {
    border-color: #ff365d;
}

#alertDialog[alertType="error"] #alertIcon {
    color: #ff365d;
}

#alertDialog[alertType="error"] #alertTitle {
    color: #ff6d89;
}

#alertDialog[alertType="error"] #alertMessage {
    color: #a35c6d;
}

#alertDialog[alertType="error"] #alertAccent {
    background-color: #ff365d;
}

#alertDialog[alertType="error"] #alertTypeLabel {
    color: #ff365d;
}


/* AUTHENTICATED */

#alertDialog[alertType="authenticated"] {
    border-color: #00ffb3;
}

#alertDialog[alertType="authenticated"] #alertIcon {
    color: #00ffb3;
}

#alertDialog[alertType="authenticated"] #alertTitle {
    color: #7affd4;
}

#alertDialog[alertType="authenticated"] #alertMessage {
    color: #5f9e89;
}

#alertDialog[alertType="authenticated"] #alertAccent {
    background-color: #00ffb3;
}

#alertDialog[alertType="authenticated"] #alertTypeLabel {
    color: #00ffb3;
}


/* AUTHENTICATION FAILED */

#alertDialog[alertType="authentication_failed"] {
    border-color: #ff365d;
}

#alertDialog[alertType="authentication_failed"] #alertIcon {
    color: #ff365d;
}

#alertDialog[alertType="authentication_failed"] #alertTitle {
    color: #ff718c;
}

#alertDialog[alertType="authentication_failed"] #alertMessage {
    color: #a15c6c;
}

#alertDialog[alertType="authentication_failed"] #alertAccent {
    background-color: #ff365d;
}

#alertDialog[alertType="authentication_failed"] #alertTypeLabel {
    color: #ff365d;
}


/* CAMERA */

#alertDialog[alertType="camera"] {
    border-color: #00cfff;
}

#alertDialog[alertType="camera"] #alertIcon {
    color: #00cfff;
}

#alertDialog[alertType="camera"] #alertTitle {
    color: #7deaff;
}

#alertDialog[alertType="camera"] #alertMessage {
    color: #5e91a3;
}

#alertDialog[alertType="camera"] #alertAccent {
    background-color: #00cfff;
}

#alertDialog[alertType="camera"] #alertTypeLabel {
    color: #00dffc;
}


/* =========================================================
   ALERT BUTTONS
   ========================================================= */

QPushButton#alertPrimaryButton {
    background-color: #007f96;
    color: #ffffff;
    border: 1px solid #00dffc;
    border-radius: 7px;
    padding: 9px 22px;
    font-weight: 700;
}

QPushButton#alertPrimaryButton:hover {
    background-color: #009db8;
    border-color: #62ffff;
}

QPushButton#alertPrimaryButton:pressed {
    background-color: #00687d;
}

QPushButton#alertSecondaryButton {
    background-color: #0b151e;
    color: #83a4b2;
    border: 1px solid #203b49;
    border-radius: 7px;
    padding: 9px 22px;
    font-weight: 600;
}

QPushButton#alertSecondaryButton:hover {
    background-color: #10232e;
    color: #d8faff;
    border-color: #38768b;
}


/* =========================================================
   MESSAGE BOXES
   ========================================================= */

QMessageBox {
    background-color: #070d14;
    border: 1px solid #173243;
}

QMessageBox QLabel {
    color: #dffaff;
}

QMessageBox QPushButton {
    background-color: #0c1922;
    color: #cceef5;
    border: 1px solid #214252;
    border-radius: 7px;
    padding: 8px 18px;
    min-width: 70px;
}

QMessageBox QPushButton:hover {
    background-color: #102a36;
    color: #ffffff;
    border-color: #00cfe8;
}


/* =========================================================
   TOOLTIPS
   ========================================================= */

QToolTip {
    background-color: #07141c;
    color: #b9f7ff;
    border: 1px solid #00bcd4;
    padding: 6px 9px;
    font-size: 11px;
}


/* =========================================================
   SETTINGS / ABOUT
   ========================================================= */

#aboutCard {
    background-color: #09121b;
    border: 1px solid #173243;
    border-radius: 12px;
}

#aboutTitle {
    color: #00eaff;
    font-size: 18px;
    font-weight: 800;
}

#aboutText {
    color: #648291;
    font-size: 12px;
}

#developerStamp {
    color: #00ffb3;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* =====================================================
   SETTINGS — REMOVE ROW / ZEBRA EFFECT
   ===================================================== */

#contentCard,
#contentCard QWidget,
#contentCard QLabel {
    background-color: transparent;
}

/* Restore the card itself */
QFrame#contentCard {
    background-color: #0a111a;
    border: 1px solid #162b3a;
    border-radius: 12px;
}

/* Text inside cards */
QFrame#contentCard QLabel {
    background-color: transparent;
    border: none;
}

/* =====================================================
   SETTINGS — REMOVE ROW / ZEBRA EFFECT
   ===================================================== */

#contentCard,
#contentCard QWidget,
#contentCard QLabel {
    background-color: transparent;
}

/* Restore the card itself */
QFrame#contentCard {
    background-color: #0a111a;
    border: 1px solid #162b3a;
    border-radius: 12px;
}

/* Text inside cards */
QFrame#contentCard QLabel {
    background-color: transparent;
    border: none;
}

/* =====================================================
   CONTENT CARDS
   ===================================================== */

#contentCard {
    background-color: #0a111a;
    border: 1px solid #162b3a;
    border-radius: 12px;
}

#contentCard QLabel {
    background-color: transparent;
    border: none;
}

#cardTitle {
    background-color: transparent;
    color: #dffaff;
    font-size: 16px;
    font-weight: 700;
}

#cardText {
    background-color: transparent;
    color: #638091;
    font-size: 13px;
}

#fieldLabel {
    background-color: transparent;
    color: #d8edf4;
    font-size: 12px;
    font-weight: 600;
}

#settingValue {
    background-color: transparent;
    color: #00eaff;
    font-size: 14px;
    font-weight: 700;
}

#diagnosticText {
    background-color: transparent;
    color: #8fa8b7;
    font-size: 12px;
}

/* =========================================================
   DISABLED UI
   ========================================================= */

QWidget:disabled {
    color: #334b58;
}

QPushButton:disabled {
    background-color: #0a1118;
    color: #304653;
    border-color: #162832;
}

/* =====================================================
   APPLICATION FOOTER
   ===================================================== */

#applicationFooter {
    background-color: #070b12;
    border-top: 1px solid #122431;
    color: #45616f;
}

#footerLeft {
    color: #45616f;
    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 500;
}

#footerAccent {
    color: #00aeca;
    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

#footerRight {
    color: #345263;
    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QFrame#innerCard {
    background-color: #081018;
    border: 1px solid #172b38;
    border-radius: 6px;
}
QLabel#authScore {
    font-size: 30px;
    font-weight: 700;
    color: #00e5ff;
}
#authUser {
    font-size: 24px;
    font-weight: 700;
    color: #00e5ff;
    padding: 8px 0;
}

#authUserVerified {
    font-size: 19px;
    font-weight: 700;
    color: #00e5ff;
    padding: 6px 0;
}

#authUserUnknown {
    font-size: 19px;
    font-weight: 700;
    color: #ff3b5c;
    padding: 6px 0;
}

"""


def get_app_stylesheet() -> str:
    """Return the application's centralized Qt stylesheet."""
    return APP_STYLE