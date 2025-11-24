# CleanUp Tool Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # GUI dependencies
    xvfb \
    x11vnc \
    fluxbox \
    # System utilities
    procps \
    # For conda (if needed)
    wget \
    curl \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs backups config

# Set environment variables
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expose VNC port (optional, for remote access)
EXPOSE 5900

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF' && chmod +x /app/entrypoint.sh
#!/bin/bash
set -e

# Start Xvfb in background if DISPLAY is :99
if [ "$DISPLAY" = ":99" ]; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    export DISPLAY=:99
    # Start window manager
    fluxbox > /dev/null 2>&1 &
fi

# Run the application
exec python main.py
EOF

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]

