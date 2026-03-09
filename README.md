# PCBA Defect Detection System

A Flask + YOLO based full-stack web application for PCBA defect detection, result visualization, and inspection record management.

## Repository Name Suggestion

Recommended GitHub repository name: `pcba-defect-detection-system`

This name is concise, descriptive, and follows common open-source naming style.

## Features

- Image upload and defect detection
- Bounding-box visualization for detection results
- Inspection history query and deletion
- Basic statistics API for result analysis
- SQLite persistence for detection records

## Tech Stack

- Backend: Flask, Flask-CORS, Flask-SQLAlchemy
- AI Inference: Ultralytics YOLO, OpenCV
- Frontend: HTML, CSS, JavaScript
- Database: SQLite

## Project Structure

```text
.
|- backend/                 Flask backend service
|- frontend/                Web frontend pages and scripts
|- models/                  YOLO model files (e.g. best.pt)
|- database/                SQLite database directory
|- uploads/                 Uploaded images and detection outputs
|- run.py                   Project startup entry
|- requirements.txt         Python dependencies
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare model file

Place your trained YOLO model in:

```text
models/best.pt
```

### 3. Run service

```bash
python run.py
```

Open in browser:

```text
http://localhost:5000
```

## API Endpoints

- `POST /api/detect` Upload image and run detection
- `GET /api/records` Get inspection history
- `GET /api/records/<id>` Get one record by id
- `DELETE /api/records/<id>` Delete one record
- `GET /api/statistics` Get statistics summary

## Development Notes

- `database/*.db` is ignored by default.
- `uploads/images/*` and `uploads/results/*` are ignored (except `.gitkeep`).
- For production deployment, use environment variables for secrets and consider PostgreSQL instead of SQLite.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
