# AIY VoiceKit 2 - Claude AI Voice Assistant

A voice assistant built on Google AIY VoiceKit 2 hardware with Claude AI integration and persistent conversation history.

## Features

- Voice control via AIY VoiceKit 2 hardware
- Claude AI integration for natural conversations
- Persistent conversation history across sessions
- Full hardware integration (LED feedback, button control, audio I/O)
- Optimized for Raspberry Pi Lite OS

## Hardware Requirements

- Google AIY VoiceKit 2 (Voice Bonnet)
- Kit components (microphone, speaker, button, LED)
- Raspberry Pi Zero WH
- MicroSD card (minimum 8 GB)

## Important Prerequisites

**This project requires proprietary Google AIY drivers and Python libraries that are no longer officially available.** These must be extracted from an old official AIY image.

### Required Google Components (not included in this repository):

**Driver Packages and pico2wave:**
- `aiy-dkms_2.0-1_all.deb`
- `aiy-overlay-voice_1.0-1_all.deb`
- `aiy-voicebonnet-soundcard-dkms_3.0-1_all.deb`
- `aiy-io-mcu-firmware_1.0-1_all.deb`
- `aiy-voice-services_1.1-1_all.deb`
- `aiy-python-wheels_1.4-1_all.deb`
- `leds-ktd202x-dkms_1.2-1_all.deb`
- `pwm-soft-dkms_2.0-1_all.deb`
- `libttspico0_1.0+git20130326-3+rpi1_armhf.deb`
- `libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb`
- `libttspico-data_1.0+git20130326-9_all.deb`

**Python Libraries:**
- AIY Python modules from `AIY-projects-python/src`

### Obtaining Components:
1. Download official AIY Voice Kit image (2021)
2. Extract .deb packages using `dpkg-repack`
3. Copy `AIY-projects-python` directory

## Installation

### Step 1: Base System

Install Raspberry Pi OS Lite (tested with 2023-05 Buster) and assemble AIY hardware following the official guide.

### Step 2: System Dependencies

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y dkms raspberrypi-linux-headers python3-pip pulseaudio flac
sudo pip3 install inotify SpeechRecognition requests
```

### Step 3: AIY Drivers + pico2wave (Manual Installation Required)

```bash
# Copy your AIY packages to a directory, then:
sudo dpkg -i aiy-dkms_2.0-1_all.deb
sudo dpkg -i aiy-overlay-voice_1.0-1_all.deb
sudo dpkg -i aiy-voicebonnet-soundcard-dkms_3.0-1_all.deb
sudo dpkg -i aiy-io-mcu-firmware_1.0-1_all.deb
sudo dpkg -i aiy-voice-services_1.1-1_all.deb
sudo dpkg -i aiy-python-wheels_1.4-1_all.deb
sudo dpkg -i leds-ktd202x-dkms_1.2-1_all.deb
sudo dpkg -i pwm-soft-dkms_2.0-1_all.deb
sudo dpkg -i libttspico0_1.0+git20130326-3+rpi1_armhf.deb
sudo dpkg -i libttspico-data_1.0+git20130326-9_all.deb  
sudo dpkg -i libttspico-utils_1.0+git20130326-3+rpi1_armhf.deb
```

### Step 4: System Configuration

```bash
echo "gpu_mem=128" | sudo tee -a /boot/config.txt
echo "dtoverlay=spi0-1cs,cs0_pin=7" | sudo tee -a /boot/config.txt
sudo sed -i -e "s/^dtparam=audio=on/#\0/" /boot/config.txt
sudo mkdir -p /etc/pulse/daemon.conf.d/
echo "default-sample-rate = 48000" | sudo tee /etc/pulse/daemon.conf.d/aiy.conf
```

### Step 5: Enable Services

```bash
sudo systemctl enable aiy_io_permission.service
sudo systemctl enable aiy_voice_classic.service
sudo systemctl start aiy_io_permission.service
sudo systemctl start aiy_voice_classic.service
sudo reboot
```

### Step 7: Project Installation

```bash
git clone https://github.com/schmidtalexomat/AIY-VoiceKit2.ClaudeAI
cd AIY-V*

# Copy your AIY-projects-python directory here
cp -r /path/to/AIY-projects-python .

# Create API key file
echo "your-claude-api-key-here" > key
```

### Step 8: Audio Test

```bash
# Set audio levels
amixer sset 'Master' 70%
amixer sset 'Capture' 70%

# Test audio (requires AIY-projects-python)
export PYTHONPATH="~/whatever/AIY-projects-python/src:$PYTHONPATH"
python3 AIY-projects-python/checkpoints/check_audio.py
```

## Usage

```bash
# Start assistant inside your AIY-dir
python3 main.py

# Run in background with logging
nohup python3 -u main.py > voice_$(date +%Y%m%d_%H%M%S).log 2>&1 &
tail -f voice*.log  # View live output
```

**Controls:**
- Press button: Start recording
- Release button: Stop recording and process
- LED colors:
  - Dimmed green: Ready
  - Red blinking: Recording
  - Purple blinking: Speech recognition
  - Blue blinking: Claude processing

## Configuration

Edit `config.py` to adjust settings:

```python
# Claude API
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 666
MAX_CONVERSATION_TURNS = 10

# Audio
SAMPLE_RATE = 16000
TEMP_AUDIO_FILE = "/tmp/voicerec.wav"

# Paths
PYTHON_PATH = os.path.join(script_dir, "AIY-projects-python/src")
```

## Project Structure

```
├── main.py                 # Main program
├── audio_system.py         # Audio recording and TTS
├── voice_recognition.py    # Speech recognition
├── claude_client.py        # Claude AI integration
├── config.py               # Configuration
├── key                     # Claude API key (create this)
├── AIY-projects-python/    # AIY Python libraries (copy here)
└── scripts/
    └── install.sh          # Installation script    
    └── test_hardware.py    # Hardware test script
    
```

## Contributing

Contributions welcome, especially:
- Improved installation automation
- Better error handling
- Multi-language support
- Alternative TTS engines

## License

MIT License - see LICENSE for details.

**Note:** This license applies only to code in this repository. Google AIY components are subject to their own licensing terms.

## Acknowledgments

- Google for the original AIY Voice Kit
- Anthropic for Claude AI API
- Raspberry Pi Foundation
