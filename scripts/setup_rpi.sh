#!/bin/bash
# Waveshare E-Paper Dashboard Setup Script for Raspberry Pi
# v0.2.0
# Run with: bash setup_rpi.sh

set -e  # Exit on error

echo "=========================================="
echo "Waveshare E-Paper Dashboard Setup (v0.2.0)"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$HOME/epaper-calendar"
VENV_DIR="$PROJECT_DIR/venv"
SYSTEMD_DIR="/etc/systemd/system"

# Check if running on RPi
echo -e "${YELLOW}[1] Detecting platform...${NC}"
if ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    echo -e "${RED}Warning: Not running on Raspberry Pi (Broadcom chipset not detected)${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies
echo -e "${YELLOW}[2] Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    libopenjp2-7 \
    libtiff5 \
    libjasper1 \
    libharfbuzz0b \
    libwebp6 \
    libatlas-base-dev

# Install SPI dependencies (required for e-paper display)
echo -e "${YELLOW}[3] Installing display drivers...${NC}"
sudo apt-get install -y \
    python3-spidev \
    python3-pip

# Install Waveshare e-paper driver
echo -e "${YELLOW}[4] Installing Waveshare libraries...${NC}"
pip3 install --upgrade pip setuptools wheel
pip3 install RPi.GPIO spidev

# Clone or update repository (if not already present)
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}[5] Cloning repository...${NC}"
    git clone https://github.com/yourusername/epaper-calendar.git "$PROJECT_DIR"
else
    echo -e "${YELLOW}[5] Updating existing repository...${NC}"
    cd "$PROJECT_DIR"
    git pull origin main
fi

# Create virtual environment
echo -e "${YELLOW}[6] Creating Python virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
echo -e "${YELLOW}[7] Installing Python dependencies...${NC}"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r "$PROJECT_DIR/requirements.txt"

# Install RPi-specific packages
pip install RPi.GPIO spidev

# Setup Google OAuth credentials
echo -e "${YELLOW}[8] Setting up Google OAuth credentials...${NC}"
if [ ! -f "$PROJECT_DIR/credentials.json" ]; then
    echo -e "${YELLOW}Please download credentials.json from Google Cloud Console${NC}"
    echo -e "${YELLOW}Place it in: $PROJECT_DIR/credentials.json${NC}"
    read -p "Press Enter once credentials.json is in place..."
fi

# Generate token
if [ ! -f "$PROJECT_DIR/token.json" ]; then
    echo -e "${YELLOW}Generating OAuth token...${NC}"
    cd "$PROJECT_DIR"
    python3 scripts/setup_oauth.py
fi

# Copy configuration file
echo -e "${YELLOW}[9] Setting up configuration...${NC}"
if [ ! -f "$PROJECT_DIR/config/dashboard.yaml" ]; then
    mkdir -p "$PROJECT_DIR/config"
    cp "$PROJECT_DIR/config/default.yaml" "$PROJECT_DIR/config/dashboard.yaml"
    echo -e "${YELLOW}Edit $PROJECT_DIR/config/dashboard.yaml with your settings${NC}"
    read -p "Press Enter once configuration is complete..."
fi

# Setup systemd service
echo -e "${YELLOW}[10] Installing systemd service...${NC}"
sudo cp "$PROJECT_DIR/systemd/waveshare-dashboard.service" "$SYSTEMD_DIR/"
sudo cp "$PROJECT_DIR/systemd/waveshare-dashboard.timer" "$SYSTEMD_DIR/"

# Fix ownership
sudo chown pi:pi -R "$PROJECT_DIR"
sudo chmod 755 "$PROJECT_DIR"

# Enable and start service
echo -e "${YELLOW}[11] Enabling systemd timer...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable waveshare-dashboard.timer
sudo systemctl enable waveshare-dashboard.service

# Start the service
echo -e "${YELLOW}[12] Starting dashboard service...${NC}"
sudo systemctl start waveshare-dashboard.timer

# Test run
echo -e "${YELLOW}[13] Running initial render test...${NC}"
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
python3 -c "from src.display.templates import DefaultTemplate; print('✓ Display module loaded successfully')"

# Show status
echo -e "${GREEN}=========================================="
echo -e "Setup Complete! ✓"
echo -e "=========================================${NC}"
echo
echo "Service Status:"
sudo systemctl status waveshare-dashboard.timer --no-pager
echo
echo "View logs:"
echo "  sudo journalctl -u waveshare-dashboard.service -f"
echo
echo "Manual test render:"
echo "  cd $PROJECT_DIR && python3 src/main.py"
echo
echo "Check timer schedule:"
echo "  systemctl list-timers waveshare-dashboard.timer"
echo
echo "For full setup guide, see: $PROJECT_DIR/docs/DEPLOYMENT.md"
