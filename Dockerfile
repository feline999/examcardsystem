FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (needed for some wheels like cryptography/reportlab)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirement files first for better layer caching
COPY requirements*.txt ./

# Prefer an exact lock file if present, otherwise fall back to requirements.txt
RUN python -m pip install --upgrade pip \
	&& (pip install -r requirements-lock.txt || pip install -r requirements.txt) \
	&& pip install gunicorn

COPY . /app

RUN mkdir -p /app/generated /app/logs \
	&& groupadd -r app && useradd -r -g app app \
	&& chown -R app:app /app

USER app

ENV FLASK_ENV=production
ENV FLASK_APP=app.py

EXPOSE 5000

# Use Gunicorn with the Flask app factory: app:create_app()
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
