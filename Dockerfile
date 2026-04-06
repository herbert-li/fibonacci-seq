# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port - this is documentation only, actual port is set via PORT env var (default: 5001)
# Use docker run -p <host>:<container> -e PORT=<container> to run on different port
EXPOSE 5001

# Use gunicorn as production WSGI server
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5001} --workers ${WORKERS:-4} --timeout 30 --access-logfile - --error-logfile - app:app"]
