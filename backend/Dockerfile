# plugins/regul_aite/backend/Dockerfile
FROM python:3.11-slim-bullseye AS base

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Set working directory
WORKDIR /app

# Install security updates and necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Basic utilities
    curl wget ca-certificates gnupg lsb-release software-properties-common \
    # Build tools
    build-essential pkg-config cmake python3-dev \
    # MariaDB dependencies
    && mkdir -p /etc/apt/keyrings \
    && wget -qO- https://mariadb.org/mariadb_release_signing_key.asc | gpg --dearmor > /etc/apt/keyrings/mariadb.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/mariadb.gpg] https://mirrors.xtom.com/mariadb/repo/10.6/ubuntu focal main" > /etc/apt/sources.list.d/mariadb.list \
    && apt-get update \
    && apt-get install -y \
    default-libmysqlclient-dev \
    default-mysql-client \
    libmariadb-dev-compat \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Trivy for container scanning
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y trivy --fix-missing && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements file for dependency scanning
COPY requirements.txt /app/

# Configure pip to be more resilient
RUN echo "[global]\ntimeout = 20\nretries = 5" > /etc/pip.conf && \
    pip install --upgrade pip setuptools wheel

# Base requirements
RUN pip install --no-cache-dir --use-pep517 --root-user-action=ignore -r /app/requirements.txt


# Install spaCy and download models
RUN python -c "from sentence_transformers import SentenceTransformer; \
                SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); \
                from sentence_transformers import CrossEncoder; \
                CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')"


# Install dependency scanning tools and scan dependencies
# RUN pip install --upgrade pip && \
    # pip install --no-cache-dir pip-audit safety && \
    # Run safety scan to identify vulnerabilities in dependencies
    # safety scan -r requirements.txt --root-user-action --full-report || true && \
    # Run pip-audit for a more comprehensive scan
    # pip-audit -r requirements.txt || true && \
    # Install requirements after checking
    # Add a debugging layer to see exactly what's happening
    # Clean up scanning tools after use
    # pip uninstall -y pip-audit safety

# Scan the base image for vulnerabilities
RUN trivy image python:3.11-slim-bullseye --no-progress --exit-code 0 || true

# Copy application code
COPY . /app/

# Run a security scan on the application code
RUN trivy fs /app --exit-code 0 || true

# Set proper permissions
RUN chmod -R 755 /app && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Health check to verify service is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Development stage
FROM base AS development

WORKDIR /app

# Copy everything from the base stage
COPY --from=0 /app /app
COPY --from=0 /usr/local /usr/local

# Development-specific setup
USER root

# Configure pip to be more resilient
RUN pip install --upgrade pip setuptools wheel debugpy watchdog pytest


# For development, we usually need hot reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--reload-dir", "/app"]

# Production stage
FROM base AS production

WORKDIR /app

# Copy everything from the base stage
COPY --from=0 /app /app
COPY --from=0 /usr/local /usr/local

# Production hardening
USER appuser
# For production, we use multiple workers for better performance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
