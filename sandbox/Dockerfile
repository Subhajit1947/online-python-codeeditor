# sandbox/Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create sandbox directory
RUN mkdir -p /sandbox
WORKDIR /sandbox

# Copy the sanitized runner
COPY sanitized_runner.py .

# Install minimal dependencies
RUN pip install --no-cache-dir --upgrade pip

# Create a non-root user
RUN useradd -m sandboxuser && \
    chown -R sandboxuser:sandboxuser /sandbox

USER sandboxuser

# Set entrypoint
ENTRYPOINT ["python", "/sandbox/sanitized_runner.py"]