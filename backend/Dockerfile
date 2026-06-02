# Stage 1: builder
FROM python:3.13-slim AS builder

WORKDIR /build

# Create a minimal app/ so setuptools can resolve the package
COPY pyproject.toml .
RUN mkdir -p app && touch app/__init__.py

# Install all dependencies (and the package itself)
RUN pip install --no-cache-dir --no-warn-script-location .

# Stage 2: runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy only installed packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy actual application code
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
