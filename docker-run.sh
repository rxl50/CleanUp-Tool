#!/bin/bash
# Convenience script to run CleanUp Tool in Docker

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}CleanUp Tool - Docker Runner${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Build image if it doesn't exist
if ! docker images | grep -q cleanup-tool; then
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t cleanup-tool .
    echo ""
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - Use X11 forwarding
    echo -e "${GREEN}Running with X11 forwarding (Linux)${NC}"
    
    # Allow X11 connections
    xhost +local:docker 2>/dev/null || echo -e "${YELLOW}Warning: Could not set xhost. GUI may not work.${NC}"
    
    docker run -it --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v $HOME/.conda:/root/.conda:ro \
        -v $HOME/.cache/pip:/root/.cache/pip:rw \
        -v $(pwd)/backups:/app/backups \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/config:/app/config \
        cleanup-tool

elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows - Use VNC or suggest native run
    echo -e "${YELLOW}Windows detected. For best results, run natively with: python main.py${NC}"
    echo -e "${YELLOW}Or use WSL2 with X Server. See DOCKER.md for details.${NC}"
    echo ""
    echo "Running with VNC (connect to localhost:5900 with VNC viewer)..."
    
    docker run -it --rm \
        -p 5900:5900 \
        -v $(pwd)/backups:/app/backups \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/config:/app/config \
        cleanup-tool

else
    # Mac or other
    echo -e "${GREEN}Running with X11 forwarding${NC}"
    
    docker run -it --rm \
        -e DISPLAY=host.docker.internal:0 \
        -v $(pwd)/backups:/app/backups \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/config:/app/config \
        cleanup-tool
fi

