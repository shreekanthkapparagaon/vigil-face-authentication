# VIGIL — Face Authentication System

A futuristic, local biometric authentication system built with **Python, PySide6, OpenCV, YuNet, SFace, and SQLite**.

VIGIL provides real-time face detection, biometric enrollment, face recognition, identity management, and authentication through a modern desktop interface.

## Features

- 🔐 **Biometric Face Authentication**
  - Real-time face verification using SFace embeddings.
  - Cosine similarity based identity matching.
  - Authentication status and similarity score displayed in real time.
- 👤 **Identity Management**
  - Register new biometric identities.
  - Automatically generated unique user codes.
  - View, edit, and delete identities.
  - Search registered users.
  - View detailed user information.
- 📸 **Biometric Enrollment**
  - Captures multiple face samples through the camera.
  - Requires exactly one visible face during enrollment.
  - Generates biometric embeddings from captured samples.
  - Stores biometric profiles locally.
- 👁️ **Face Detection**
  - Uses the **YuNet** face detector.
  - Optimized for real-time camera processing.
- 🧠 **Face Recognition**
  - Uses the **SFace** recognition model.
  - Pre-trained recognition model — user registration does **not retrain the model**.
  - Face images are processed to generate biometric embeddings.
- 📊 **System Dashboard**
  - Registered identity count, engine status, camera status, security status, runtime diagnostics, engine configuration, and quick-access controls.
- ⚙️ **System Settings**
  - Recognition threshold, detection scale, engine/database information, embedding cache, system status, application information, developer information, and maintenance tools.
- 🖥️ **Modern Desktop UI**
  - Built with PySide6.
  - Dark futuristic interface with neon cyan biometric/security styling.
  - Console-inspired typography.

## How It Works

VIGIL uses a pre-trained face detection and recognition pipeline.

```text
                  CAMERA
                     │
                     ▼
              ┌─────────────┐
              │    YuNet    │
              │ Face Detect │
              └──────┬──────┘
                     │
                     ▼
               Detected Face
                     │
                     ▼
              ┌─────────────┐
              │    SFace    │
              │ Recognition │
              └──────┬──────┘
                     │
                     ▼
              Face Embedding
                     │
          ┌──────────┴──────────┐
          │                     │
       ENROLLMENT          AUTHENTICATION
          │                     │
          ▼                     ▼
   Store Embedding       Compare Embeddings
                                │
                                ▼
                       Cosine Similarity
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                       MATCH        NO MATCH
                         │             │
                         ▼             ▼
                     VERIFIED       UNKNOWN
```

### Enrollment

```text
Camera
  ↓
Multiple face samples
  ↓
Face detection
  ↓
SFace embedding generation
  ↓
Biometric profile
  ↓
SQLite database
  ↓
Embedding cache
```

The application **does not train the SFace model for every new user**. It generates a biometric representation of the user's face and stores that representation.

### Authentication

```text
Live camera frame
       ↓
Face detection
       ↓
Face embedding
       ↓
Compare with registered embeddings
       ↓
Cosine similarity
       ↓
Threshold evaluation
       ↓
Identity verified / rejected
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| GUI | PySide6 |
| Computer Vision | OpenCV |
| Face Detection | YuNet |
| Face Recognition | SFace |
| Database | SQLite |
| Biometric Representation | Float32 normalized embeddings |
| Matching | Cosine similarity |
| Environment | `uv` |
| Packaging | PyInstaller |

## Project Structure

```text
Face-Authentication/
│
├── app/
│   ├── assets/
│   │   ├── icon.ico
│   │   └── icon.png
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── camera_widget.py
│   │   └── ...
│   ├── ...
│   └── __main__.py
│
├── data/
│   ├── *.onnx
│   └── .gitkeep
│
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

> The exact internal modules may evolve as the project develops.

## Requirements

- Windows 10/11
- Python 3.11+ recommended
- Webcam
- Dependencies defined in `pyproject.toml`
- YuNet and SFace `.onnx` model files

## Installation

Clone the repository:

```bash
git clone https://github.com/shreekanthkapparagaon/Face-Authentication.git
cd Face-Authentication
```

Sync the project environment using `uv`:

```bash
uv sync
```

Make sure the required ONNX models are available inside:

```text
data/
```

## Running the Application

```bash
uv run python -m app
```

## Biometric Data

VIGIL is designed as a **local biometric authentication system**.

During enrollment, camera frames are temporarily processed to generate biometric embeddings. The recognition process is based on numerical face embeddings rather than continuously training a model.

The local system uses:

```text
SQLite
   +
Biometric Embeddings
   +
Local Embedding Cache
```

The local database and runtime biometric data are intentionally excluded from Git through `.gitignore`.

The required `.onnx` detection and recognition models remain part of the application's runtime requirements.

## Security & Privacy

VIGIL is designed around local processing.

- Face recognition is performed locally.
- Authentication data is stored locally.
- No cloud authentication service is required.
- Database files are excluded from source control.
- Runtime biometric data should never be committed to Git.
- Required model files are kept separately from generated biometric data.

**Important:** Biometric embeddings are sensitive data. Protect the application's database and runtime data directory appropriately when deploying the system.

## Application Interface

```text
SYSTEM OVERVIEW
│
├── Dashboard
│   ├── System Summary
│   ├── Quick Actions
│   ├── System Diagnostics
│   ├── Engine Information
│   └── Security Status
│
├── Register Identity
│   ├── Camera
│   ├── Identity Information
│   ├── Biometric Capture
│   └── Enrollment Status
│
├── Identity Authentication
│   ├── Live Camera
│   ├── Authentication Status
│   ├── Similarity Score
│   └── Matched Identity
│
├── Users
│   ├── Search
│   ├── Identity List
│   ├── View
│   ├── Edit
│   └── Delete
│
└── Settings
    ├── Recognition Engine
    ├── Vision Engine
    ├── Database
    ├── System Status
    ├── Application Information
    ├── Developer Information
    └── Maintenance
```

## Windows Executable

VIGIL can be packaged as a Windows executable using **PyInstaller**.

Application icon:

```text
app/assets/icon.ico
```

Application artwork:

```text
app/assets/icon.png
```

When packaging the application, the ONNX models and required assets must also be included in the final build.

## Configuration

Important biometric configuration values include:

```text
Face match threshold
Face detection scale
```

These values control the recognition and detection pipeline and are displayed in the **Settings** section.

## Development

Run the application:

```bash
uv run python -m app
```

Run tests:

```bash
uv run pytest
```

## Project Status

**Version:** `1.0.0`  
**Status:** Active Development

VIGIL is being developed as a local desktop biometric authentication platform.

## Author

**Shreekanth Kapparagaon**

VIGIL Face Authentication System

Built with Python, PySide6, OpenCV, YuNet, SFace, and SQLite.

## License

This project is currently under development. License information will be added when the project license is finalized.
