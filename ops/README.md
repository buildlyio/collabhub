# CollabHub Operations Scripts

This directory contains operational scripts for managing the CollabHub development environment.

## startup.sh - Development Server Management

A comprehensive script to manage your local development environment.

### Features

- ✅ Automatic virtual environment setup and management
- ✅ Dependency installation and updates
- ✅ Database migration management
- ✅ Server start/stop/restart with PID tracking
- ✅ Status monitoring and logging

### First Time Setup

```bash
./ops/startup.sh setup
```

This will:
1. Create a virtual environment at `.venv/`
2. Install all dependencies from `requirements.txt`
3. Run database migrations

### Daily Usage

**Start the server:**
```bash
./ops/startup.sh start
```

**Stop the server:**
```bash
./ops/startup.sh stop
```

**Restart the server:**
```bash
./ops/startup.sh restart
```

**Check server status:**
```bash
./ops/startup.sh status
```

### What the Script Does

#### Start Command
- Checks if virtual environment exists (creates if missing)
- Activates the virtual environment
- Updates dependencies if `requirements.txt` has changed
- Runs any pending database migrations
- Starts Django development server on port 8000
- Saves process ID for management
- Logs output to `ops/dev_server.log`

#### Stop Command
- Gracefully stops the running server
- Cleans up PID file
- Force kills if necessary

#### Restart Command
- Stops the server if running
- Starts a fresh server instance

#### Status Command
- Shows if server is running
- Displays PID and URL
- Shows last 5 log lines

### Server URLs

- Main application: http://127.0.0.1:8000
- Admin interface: http://127.0.0.1:8000/admin
- Dashboard: http://127.0.0.1:8000/onboarding/dashboard/

### Log Files

Server logs are written to: `ops/dev_server.log`

View logs in real-time:
```bash
tail -f ops/dev_server.log
```

### Environment Variables

The script uses `mysite.settings.dev` by default. To use different settings:

```bash
# Edit dev.sh and change this line:
SETTINGS_MODULE="mysite.settings.dev"
```

### Troubleshooting

**Server won't start:**
```bash
# Check the logs
cat ops/dev_server.log

# Force clean restart
./ops/startup.sh stop
rm -f ops/.dev_server.pid
./ops/startup.sh start
```

**Dependencies not installing:**
```bash
# Manually activate venv and update
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Start server again
./ops/startup.sh start
```

### Requirements

- Python 3.8-3.10 (Django 3.2 compatibility)
- **Note:** Python 3.11+ is not supported by Django 3.2. Use Python 3.10 or upgrade Django to 4.2+
- macOS/Linux (zsh/bash)
- Write permissions in project directory

### Notes

- The script creates a `.venv` directory for the virtual environment
- PID file is stored at `ops/.dev_server.pid`
- Server logs are stored at `ops/dev_server.log`
- Default port is 8000 (can be changed in the script)
