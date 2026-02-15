FROM python:3.11-slim-bookworm

# Install system dependencies (same as prod)
# We need git/procps for consistency, though maybe not strict requirement for unit tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (Prod + Test)
COPY requirements.txt .
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Install Playwright browsers and their system dependencies
# We only install chromium to keep the image size manageable
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy App and Tests
COPY app/ app/
COPY tests/ tests/
COPY run.py .

# Run Tests
# -vv: verbose
# --cov: coverage
# --cov-fail-under=90: Fail if coverage is below 90%
CMD ["python3", "-m", "pytest", "-vv", "--cov=app", "--cov-fail-under=90"]
