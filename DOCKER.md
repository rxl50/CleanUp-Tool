# Docker Setup for CleanUp Tool

This guide explains how to run CleanUp Tool in a Docker container.

## ⚠️ Important Notes

**Dockerizing a GUI application that needs to access system files is complex.** The CleanUp tool is designed to run directly on your system to access:
- Conda environments
- System temp files
- Browser caches
- User directories

Running in Docker has limitations:
- May not access all host system files
- GUI requires X11 forwarding or VNC
- Some cleanup operations may not work as expected

**Recommendation:** For best results, run the application directly on your host system.

## Prerequisites

- Docker installed and running
- Docker Compose (optional, for easier management)

## Quick Start

### Build the Docker Image

```bash
docker build -t cleanup-tool .
```

### Run the Container

#### Option 1: With X11 Forwarding (Linux)

```bash
# Allow X11 connections
xhost +local:docker

# Run container
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $HOME/.conda:/root/.conda:ro \
  -v $(pwd)/backups:/app/backups \
  -v $(pwd)/logs:/app/logs \
  cleanup-tool
```

#### Option 2: With VNC (Cross-platform)

```bash
docker run -it --rm \
  -p 5900:5900 \
  -v $(pwd)/backups:/app/backups \
  -v $(pwd)/logs:/app/logs \
  cleanup-tool
```

Then connect with a VNC viewer to `localhost:5900`

#### Option 3: Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Windows Setup

### Using WSL2

1. **Install WSL2 and Docker Desktop for Windows**

2. **Install X Server for Windows:**
   - Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [X410](https://x410.dev/)

3. **Configure X Server:**
   - Start X Server
   - Allow connections from network
   - Note the DISPLAY variable (usually `localhost:0`)

4. **Run in WSL2:**
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   docker run -it --rm \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     cleanup-tool
   ```

### Using Windows Containers

Windows containers have limited GUI support. Consider using VNC instead.

## Volume Mounts

To access host files, mount relevant directories:

```bash
docker run -it --rm \
  # Conda environments (read-only recommended)
  -v $HOME/.conda:/root/.conda:ro \
  
  # Pip cache
  -v $HOME/.cache/pip:/root/.cache/pip:rw \
  
  # System temp (if you want to clean host temp)
  -v /tmp:/tmp:rw \
  
  # Application data
  -v $(pwd)/backups:/app/backups \
  -v $(pwd)/logs:/app/logs \
  
  cleanup-tool
```

## Limitations

1. **System File Access:**
   - Container may not access all Windows system directories
   - Some cleanup operations may fail

2. **Conda/Pip:**
   - Host conda/pip installations may not be accessible
   - May need to install conda/pip inside container

3. **Browser Caches:**
   - Browser cache locations are host-specific
   - May need custom volume mounts

4. **Permissions:**
   - Container runs with limited permissions
   - May need `--privileged` flag for some operations (not recommended)

## Customization

### Modify Dockerfile

Edit `Dockerfile` to:
- Install conda inside container
- Add additional system packages
- Configure environment variables

### Modify docker-compose.yml

Edit `docker-compose.yml` to:
- Add more volume mounts
- Configure network settings
- Set environment variables

## Troubleshooting

### GUI Not Displaying

**Linux:**
```bash
# Check X11 permissions
xhost +local:docker

# Verify DISPLAY variable
echo $DISPLAY
```

**Windows/WSL2:**
- Ensure X Server is running
- Check firewall settings
- Verify DISPLAY variable points to correct IP

### Permission Denied Errors

```bash
# Run with user mapping (Linux)
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  cleanup-tool
```

### Cannot Access Host Files

- Verify volume mounts are correct
- Check file permissions
- Use absolute paths for volumes

## Alternative: Development Container

For development, you can use the container as a development environment:

```bash
docker run -it --rm \
  -v $(pwd):/app \
  -v $(pwd)/backups:/app/backups \
  cleanup-tool \
  /bin/bash
```

Then run the application inside:
```bash
python main.py
```

## Security Considerations

⚠️ **Warning:** Running GUI applications in Docker with host access can have security implications:

- Don't use `--privileged` unless absolutely necessary
- Limit volume mounts to necessary directories
- Review file permissions
- Use read-only mounts where possible

## Recommendation

For production use, **run the application directly on your host system** rather than in Docker. Docker is better suited for:
- Development and testing
- Isolated environments
- CI/CD pipelines

The application is designed to run natively and will have better access to system resources.

