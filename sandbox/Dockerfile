# Python sandbox container
FROM python:3.9-slim

# Create restricted user
RUN useradd -m restricted && \
    chmod 755 /home/restricted

# Set up safe environment
WORKDIR /sandbox
COPY --chown=restricted:restricted ./sanitized_runner.py .
RUN chmod 555 /sandbox && \
    chmod 400 sanitized_runner.py

USER restricted
CMD ["python", "sanitized_runner.py"]