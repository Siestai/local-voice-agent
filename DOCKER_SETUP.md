# LiveKit Server - Docker Setup 🐳

This guide explains how to run the LiveKit server locally using Docker Compose.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)

### Install Docker Desktop

If you don't have Docker installed:

```bash
# Download from Docker website
# https://www.docker.com/products/docker-desktop

# Or install via Homebrew
brew install --cask docker
```

After installation, start Docker Desktop from your Applications folder.

## 🚀 Quick Start

### 1. Start the LiveKit Server

```bash
# Using make (recommended)
make livekit-start

# Or using docker-compose directly
docker-compose up -d
```

The server will be available at:
- **WebSocket**: `ws://localhost:7880` (for client connections)
- **HTTP API**: `http://localhost:7881` (for API calls)

### 2. Verify Server is Running

```bash
# Check status
make livekit-status

# Or check manually
curl http://localhost:7880
docker-compose ps
```

### 3. View Logs

```bash
# Follow live logs
make livekit-logs

# Or using docker-compose
docker-compose logs -f
```

### 4. Stop the Server

```bash
# Stop the server
make livekit-stop

# Or using docker-compose
docker-compose down
```

## 🔧 Configuration

### Server Configuration

The server is configured via `livekit.yaml`:

```yaml
# Key configuration options
port: 7880                    # WebSocket port
rtc:
  port_range_start: 50000    # RTP/RTCP port range
  port_range_end: 50200
keys:
  devkey: secret             # API credentials (dev only!)
room:
  auto_create: true          # Auto-create rooms
  empty_timeout: 300         # 5 minutes
dev_mode: true               # Enable dev features
```

### Environment Variables (.env)

Your voice agent connects using these credentials from `.env`:

```bash
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

**⚠️ WARNING**: These are development credentials only. Change for production!

## 📊 Available Make Commands

```bash
make livekit-start      # Start the LiveKit server
make livekit-stop       # Stop the LiveKit server
make livekit-restart    # Restart the server
make livekit-status     # Check server status
make livekit-logs       # View server logs (live)
make livekit-clean      # Remove containers and volumes
```

## 🔍 Troubleshooting

### Port Already in Use

If ports 7880 or 7881 are already in use:

```bash
# Check what's using the port
lsof -i :7880
lsof -i :7881

# Kill the process if needed
kill -9 <PID>

# Or change ports in docker-compose.yml
ports:
  - "8880:7880"  # Map to different external port
```

### Docker Not Running

```bash
# Check Docker status
docker info

# Start Docker Desktop
open -a Docker

# Wait for Docker to start (check in menu bar)
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs livekit

# Check container status
docker-compose ps

# Restart with fresh state
docker-compose down -v
docker-compose up -d
```

### Connection Refused

```bash
# Check if container is running
docker ps | grep livekit

# Check if ports are exposed
docker port livekit-server

# Test connection
curl http://localhost:7880
telnet localhost 7880
```

### UDP Ports for WebRTC

If you have issues with audio/video streaming:

1. Check firewall settings (allow ports 50000-50200/UDP)
2. Ensure UDP ports are properly mapped in docker-compose.yml
3. For production, configure proper TURN server

## 🔐 Security Notes

### Development vs Production

**Current Setup (Development)**:
- ✅ Simple setup for local testing
- ✅ No external dependencies
- ⚠️ **DO NOT USE IN PRODUCTION**
- ⚠️ Uses default credentials (devkey/secret)
- ⚠️ No TLS encryption
- ⚠️ No authentication

**Production Setup**:
```yaml
# livekit.yaml for production
keys:
  prod-key-1: "your-secure-api-secret-here"
  prod-key-2: "another-secure-secret"

# Enable TLS
port: 443
bind_addresses:
  - "0.0.0.0"

# Add TURN server
turn:
  enabled: true
  domain: turn.yourdomain.com
  tls_port: 5349

# Disable dev mode
dev_mode: false
```

### Generate Secure API Keys

```bash
# Generate random API key and secret
openssl rand -hex 32  # API Key
openssl rand -hex 32  # API Secret
```

## 📚 Docker Compose Reference

### Full docker-compose.yml Structure

```yaml
version: '3.9'
services:
  livekit:
    image: livekit/livekit-server:latest
    command: --config /etc/livekit.yaml
    ports:
      - "7880:7880"           # WebSocket
      - "7881:7881"           # HTTP API  
      - "50000-50200:50000-50200/udp"  # RTP/RTCP
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml:ro
    networks:
      - livekit-network
```

### Useful Docker Commands

```bash
# View all containers
docker ps -a

# View container logs
docker logs livekit-server

# Execute command in container
docker exec -it livekit-server sh

# View resource usage
docker stats livekit-server

# Restart single container
docker restart livekit-server

# Remove container
docker rm -f livekit-server
```

## 🔄 Updates and Maintenance

### Update LiveKit Server

```bash
# Pull latest image
docker-compose pull

# Restart with new image
docker-compose up -d
```

### Backup Configuration

```bash
# Backup current setup
make backup

# Files backed up:
# - backups/.env.YYYYMMDD_HHMMSS
# - backups/requirements.txt.YYYYMMDD_HHMMSS
# - livekit.yaml (manual backup)
```

## 🌐 Network Configuration

### Docker Network

The setup creates a dedicated Docker network (`livekit-network`):

```bash
# Inspect network
docker network inspect livekit-network

# See connected containers
docker network ls
```

### Connecting Other Services

To connect additional services (Redis, webhook servers, etc.):

```yaml
# docker-compose.yml
services:
  livekit:
    # ... existing config ...
  
  redis:
    image: redis:alpine
    networks:
      - livekit-network
```

Then update `livekit.yaml`:
```yaml
redis:
  address: redis:6379
```

## 📖 Additional Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Server Guide](https://docs.livekit.io/deploy/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [LiveKit Docker Hub](https://hub.docker.com/r/livekit/livekit-server)

## 🐛 Common Issues

### Issue: "Cannot connect to the Docker daemon"

**Solution**:
```bash
# Start Docker Desktop
open -a Docker
# Wait 30-60 seconds for Docker to fully start
```

### Issue: "Port is already allocated"

**Solution**:
```bash
# Find process using the port
lsof -i :7880
# Kill it or change docker-compose.yml port mapping
```

### Issue: "Permission denied" when accessing volumes

**Solution**:
```bash
# Fix file permissions
chmod 644 livekit.yaml
# Ensure file exists
ls -la livekit.yaml
```

### Issue: Agent can't connect to LiveKit

**Solution**:
1. Check server is running: `make livekit-status`
2. Verify .env has correct URL: `LIVEKIT_URL=ws://localhost:7880`
3. Check credentials match: `devkey` / `secret`
4. Test connection: `curl http://localhost:7880`

## 🎯 Next Steps

1. ✅ Start LiveKit server: `make livekit-start`
2. ✅ Verify it's running: `make livekit-status`
3. ✅ Check your `.env` file has correct credentials
4. ✅ Run the voice agent: `make dev`
5. 🎉 Start building!

---

**Need help?** 
- Check main README: `README.md`
- View server logs: `make livekit-logs`
- Test agent connection: `make check-env`

