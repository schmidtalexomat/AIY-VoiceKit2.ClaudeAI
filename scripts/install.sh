#!/bin/bash
# AIY VoiceKit 2 - Claude AI Voice Assistant Installation Script

set -e  # Exit on any error

echo "AIY VoiceKit 2 - Claude AI Voice Assistant Installation"
echo "====================================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Step 2: Installing system dependencies..."
sudo apt install -y \
    dkms \
    raspberrypi-linux-headers \
    python3-pip \
    pulseaudio \
    flac \
    espeak \
    espeak-data \
    git \
    wget

# Install Python dependencies
echo "Step 3: Installing Python dependencies..."
sudo pip3 install inotify SpeechRecognition requests

# Optional: Install German voice
echo "Step 4: Installing German voice (optional)..."
read -p "Install German MBROLA voice? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    wget https://raspberry-pi.fr/download/espeak/mbrola3.0.1h_armhf.deb -O mbrola.deb
    sudo dpkg -i mbrola.deb || echo "MBROLA installation may have issues, continuing..."
    sudo apt install -y mbrola-de6 || echo "German voice installation failed, continuing..."
    rm -f mbrola.deb
fi

# Check for AIY packages
echo "Step 5: Checking for AIY packages..."
if [ -d "aiy-packages" ]; then
    echo "Found aiy-packages directory. Installing AIY drivers..."
    cd aiy-packages
    
    # Check for required packages
    required_packages=(
        "aiy-dkms_2.0-1_all.deb"
        "aiy-overlay-voice_1.0-1_all.deb"
        "aiy-voicebonnet-soundcard-dkms_3.0-1_all.deb"
        "aiy-io-mcu-firmware_1.0-1_all.deb"
        "aiy-voice-services_1.1-1_all.deb"
        "aiy-python-wheels_1.4-1_all.deb"
        "leds-ktd202x-dkms_1.2-1_all.deb"
        "pwm-soft-dkms_2.0-1_all.deb"
    )
    
    missing_packages=()
    for package in "${required_packages[@]}"; do
        if [ ! -f "$package" ]; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -eq 0 ]; then
        echo "Installing AIY packages..."
        sudo dpkg -i aiy-dkms_2.0-1_all.deb
        sudo dpkg -i aiy-overlay-voice_1.0-1_all.deb
        sudo dpkg -i aiy-voicebonnet-soundcard-dkms_3.0-1_all.deb
        sudo dpkg -i aiy-io-mcu-firmware_1.0-1_all.deb
        sudo dpkg -i aiy-voice-services_1.1-1_all.deb
        sudo dpkg -i aiy-python-wheels_1.4-1_all.deb
        sudo dpkg -i leds-ktd202x-dkms_1.2-1_all.deb
        sudo dpkg -i pwm-soft-dkms_2.0-1_all.deb
        
        echo "Configuring system..."
        echo "gpu_mem=128" | sudo tee -a /boot/config.txt
        echo "dtoverlay=spi0-1cs,cs0_pin=7" | sudo tee -a /boot/config.txt
        sudo sed -i -e "s/^dtparam=audio=on/#\0/" /boot/config.txt
        sudo mkdir -p /etc/pulse/daemon.conf.d/
        echo "default-sample-rate = 48000" | sudo tee /etc/pulse/daemon.conf.d/aiy.conf
        
        echo "Enabling services..."
        sudo systemctl enable aiy_io_permission.service
        sudo systemctl enable aiy_voice_classic.service
        sudo systemctl start aiy_io_permission.service
        sudo systemctl start aiy_voice_classic.service
        
        cd ..
        AIY_INSTALLED=true
    else
        echo "Missing AIY packages:"
        for package in "${missing_packages[@]}"; do
            echo "  - $package"
        done
        AIY_INSTALLED=false
    fi
else
    echo "AIY packages directory not found."
    AIY_INSTALLED=false
fi

# Check for AIY Python libraries
echo "Step 6: Checking for AIY Python libraries..."
if [ -d "AIY-projects-python" ]; then
    echo "✓ AIY-projects-python directory found"
    AIY_PYTHON=true
else
    echo "✗ AIY-projects-python directory not found"
    AIY_PYTHON=false
fi

# Setup API key
echo "Step 7: Setting up Claude API key..."
if [ ! -f "key" ]; then
    echo "Please enter your Claude API key:"
    read -r api_key
    echo "$api_key" > key
    echo "API key saved to 'key' file"
else
    echo "✓ API key file already exists"
fi

# Set audio levels
echo "Step 8: Setting audio levels..."
amixer sset 'Master' 70% 2>/dev/null || echo "Could not set Master volume"
amixer sset 'Capture' 70% 2>/dev/null || echo "Could not set Capture volume"

# Final status
echo ""
echo "Installation Summary:"
echo "===================="
echo "System packages:     ✓ Installed"
echo "Python dependencies: ✓ Installed"

if [ "$AIY_INSTALLED" = true ]; then
    echo "AIY drivers:         ✓ Installed"
else
    echo "AIY drivers:         ✗ Not installed (manual setup required)"
fi

if [ "$AIY_PYTHON" = true ]; then
    echo "AIY Python libs:     ✓ Found"
else
    echo "AIY Python libs:     ✗ Not found (manual setup required)"
fi

echo ""
if [ "$AIY_INSTALLED" = true ] && [ "$AIY_PYTHON" = true ]; then
    echo "✓ Installation complete! Reboot recommended."
    echo ""
    echo "After reboot, test with:"
    echo "  python3 scripts/test_hardware.py"
    echo ""
    echo "Then start the assistant with:"
    echo "  python3 main.py"
    echo ""
    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
else
    echo "⚠ Installation incomplete. Manual setup required for:"
    if [ "$AIY_INSTALLED" = false ]; then
        echo "  - AIY driver packages (see README.md)"
    fi
    if [ "$AIY_PYTHON" = false ]; then
        echo "  - AIY-projects-python directory (see README.md)"
    fi
    echo ""
    echo "See README.md for manual installation instructions."
fi
