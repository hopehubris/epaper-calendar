#!/bin/bash
# Deployment script for Raspberry Pi

set -e

# Configuration
REMOTE_USER="${1:-pi}"
REMOTE_HOST="${2:-192.168.1.100}"
REMOTE_PATH="/home/pi/epaper-calendar"
LOCAL_PATH="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"

echo "=========================================="
echo "E-Paper Calendar Deployment Script"
echo "=========================================="
echo "Source: $LOCAL_PATH"
echo "Target: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo

# Check if SSH is available
if ! command -v ssh &> /dev/null; then
    echo "✗ SSH not found. Please install SSH client."
    exit 1
fi

# Check if we can connect
echo "→ Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo OK" &> /dev/null; then
    echo "✗ Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    echo "  Usage: $0 [user] [host]"
    echo "  Example: $0 pi 192.168.1.100"
    exit 1
fi
echo "✓ SSH connection OK"

# Create remote directory
echo "→ Creating remote directory..."
ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Copy project files
echo "→ Copying project files..."
rsync -avz --exclude='.git' --exclude='venv' --exclude='__pycache__' \
    --exclude='*.pyc' --exclude='.env' --exclude='token.json' \
    --exclude='events_cache.db' --exclude='credentials.json' \
    "$LOCAL_PATH/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

# Set up Python virtual environment
echo "→ Setting up Python virtual environment..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
cd /home/pi/epaper-calendar
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Copy systemd files
echo "→ Installing systemd service..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
sudo cp /home/pi/epaper-calendar/systemd/epaper-calendar.service \
    /etc/systemd/system/
sudo cp /home/pi/epaper-calendar/systemd/epaper-calendar.timer \
    /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable epaper-calendar.timer
EOF

# Create .env from .env.example
echo "→ Creating .env file..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
if [ ! -f /home/pi/epaper-calendar/.env ]; then
    cp /home/pi/epaper-calendar/.env.example /home/pi/epaper-calendar/.env
    echo "✓ Created .env - please edit with your calendar IDs"
else
    echo "✓ .env already exists"
fi
EOF

# Create log directory
echo "→ Creating log directory..."
ssh "$REMOTE_USER@$REMOTE_HOST" << 'EOF'
sudo mkdir -p /var/log/epaper-calendar
sudo chown pi:pi /var/log/epaper-calendar
EOF

echo
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Configure calendar IDs:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST"
echo "   nano $REMOTE_PATH/.env"
echo
echo "2. Set up OAuth token:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST"
echo "   cd $REMOTE_PATH"
echo "   source venv/bin/activate"
echo "   python scripts/setup_oauth.py --generate"
echo
echo "3. Test the service:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST"
echo "   systemctl start epaper-calendar"
echo "   journalctl -u epaper-calendar -f"
echo
echo "4. Enable 15-minute updates:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST"
echo "   sudo systemctl start epaper-calendar.timer"
echo "   systemctl status epaper-calendar.timer"
echo
