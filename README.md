# Exam Card System (Flask)

Minimal scaffold for a student exam card management system with validation rules.

<!-- CI status badge: replace <owner>/<repo> with your GitHub repo -->
[![CI](https://github.com/<owner>/<repo>/workflows/CI/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml)

Quick start

1. Create a virtual environment and activate it.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

Notes
- This scaffold uses SQLite by default. Set `DATABASE_URL` to a production DB.
- I chose Flask for a quick prototype. If you prefer Django or Laravel, tell me.

Seeding an admin user

After installing dependencies and creating the database, run:

```powershell
python seed.py --username admin --password your_password
```

This will create a user with the provided credentials (defaults: username `admin`, password `admin`).

Running tests

Install dev dependencies and run pytest:

```powershell
pip install -r requirements.txt
pytest -q
```

Generated files

Generated exam cards are stored in the app `generated/` directory and include a UUID in the filename to avoid collisions.

Continuous integration

This project includes a GitHub Actions workflow at `.github/workflows/ci.yml` which runs the test suite on push and pull requests.

To enable CI, push this repository to GitHub and ensure Actions are enabled for the repository.

Badge instructions: replace `<owner>/<repo>` above with your GitHub repository path (e.g. `alice/examcardsystem`).

Docker

Build and run the app with Docker (useful if Python isn't installed locally):

```powershell
docker build -t examcardsystem:latest .
docker run -p 5000:5000 --rm -v "%CD%\\generated:/app/generated" examcardsystem:latest
```

The container runs the Flask app on port 5000 and maps the host `generated/` folder so generated exam cards are available on the host.

Reproducible installs

For stable CI and production installs it's useful to pin exact package versions. Locally, after creating and activating your virtual environment, generate a lock file:

```powershell
# activate venv then
.\tools\pin_requirements.ps1
# commit requirements-lock.txt and use it in CI for reproducible builds
```

Docker volume mount examples (Windows)

PowerShell (simple):

```powershell
New-Item -ItemType Directory -Path .\generated -Force
docker run -p 5000:5000 --rm -v "${PWD}/generated:/app/generated" examcardsystem:latest
```

PowerShell (robust path normalization):

```powershell
New-Item -ItemType Directory -Path .\generated -Force
$hostPath = (Resolve-Path .\generated).Path -replace '\\','/'
docker run -p 5000:5000 --rm -v "$hostPath:/app/generated" examcardsystem:latest
```

CMD.exe:

```cmd
mkdir generated
docker run -p 5000:5000 --rm -v "%cd%/generated:/app/generated" examcardsystem:latest
```

If you do not need files on the host, use a named volume to avoid host-path issues:

```powershell
docker run -p 5000:5000 --rm -v exam_generated:/app/generated examcardsystem:latest
```

Security notes

- Set a strong `SECRET_KEY` in environment for production, e.g. `export SECRET_KEY=$(openssl rand -hex 32)`.
- CSRF protection is enabled using `Flask-WTF`; all write forms include a CSRF token.
- Session cookie settings are set to be HTTP-only and `SameSite=Lax` by default in `config.py`.

Rate limiting and security headers

- HTTP security headers are applied with `Flask-Talisman` (CSP disabled by default in the dev scaffold).
- Rate limiting is provided by `Flask-Limiter`. Default limits are set in `config.py` and the login endpoint is throttled to `5/minute`.

Content-Security-Policy and logging

- A basic Content Security Policy (CSP) is applied by default to allow the app and the CDN used for Bootstrap (`cdn.jsdelivr.net`). Adjust the policy in `app.py` if you host assets differently.
- Basic application logging is enabled; for production consider configuring file handlers, rotation, and a centralized logging/monitoring service.

Structured logging

The app now emits structured JSON logs to both console and a rotating file handler under `logs/app.log` by default. Configure the output directory and filename with `LOG_DIR` and `LOG_FILE` environment variables.

Example (Windows PowerShell):

```powershell
set LOG_DIR=.
set LOG_FILE=app.log
```

Error monitoring (Sentry)

You can enable Sentry error monitoring by setting the `SENTRY_DSN` environment variable. When provided, the app will initialize `sentry-sdk` with Flask and logging integrations.

Example (Linux/macOS):

```bash
export SENTRY_DSN="https://<key>@sentry.io/<project>"
export SENTRY_TRACES_SAMPLE_RATE=0.0
```

In GitHub Actions, add `SENTRY_DSN` as a secret and expose it to the workflow if you want CI errors reported.

CI note: the provided GitHub Actions workflow reads the `SENTRY_DSN` repository secret and injects it into the test and Docker test jobs so the application will initialize Sentry during CI runs when the secret is present.