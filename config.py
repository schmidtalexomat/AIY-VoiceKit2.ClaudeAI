# AIY VoiceKit2 + Claude AI - basic config

import os

# Claude API
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, "key"), 'r') as f:
    CLAUDE_API_KEY = f.read().strip()
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 666

# Conversation settings
MAX_CONVERSATION_TURNS = 10  # Keep last 10 exchanges

# Audio Settings
SAMPLE_RATE = 16000
TEMP_AUDIO_FILE = "/tmp/voicerec.wav"

# Paths
PYTHON_PATH = os.path.join(script_dir, "AIY-projects-python/src")
