#!/usr/bin/env python3
import sys
import time
import threading
import os

# Local modules
import config
from audio_system import AudioSystem
from voice_recognition import SpeechRecognizer
from claude_client import ClaudeClient

# AIY system setup
sys.path.insert(0, config.PYTHON_PATH)
from aiy.leds import Leds, Color, Pattern
from aiy.board import Board

class VoiceRecorder:
    def __init__(self):
        # Hardware
        self.board = Board()
        self.leds = Leds()
        
        # Button events
        self.board.button.when_pressed = self.button_pressed
        self.board.button.when_released = self.button_released
        
        # Components
        self.audio = AudioSystem()
        self.speech = SpeechRecognizer()
        self.claude = ClaudeClient()
        
        # Status
        self.running = True
        
        # Define LED patterns
        self.recording_pattern = Pattern.blink(600)
        self.recognition_pattern = Pattern.blink(800)
        self.claude_pattern = Pattern.blink(1200)
        
        # Ready - solid dim green
        self.set_ready()
        self.audio.speak_text("yo")

    def set_ready(self):
        """Ready state - solid dim green"""
        self.leds.update(Leds.rgb_on((0, 10, 0)))

    def set_recording(self):
        """Recording state - red blinking"""
        self.leds.pattern = self.recording_pattern
        self.leds.update(Leds.rgb_pattern((30, 0, 0)))

    def set_speech_recognition(self):
        """Speech recognition - purple blinking"""
        self.leds.pattern = self.recognition_pattern
        self.leds.update(Leds.rgb_pattern((30, 0, 30)))

    def set_claude_thinking(self):
        """Claude thinking - blue blinking"""
        self.leds.pattern = self.claude_pattern
        self.leds.update(Leds.rgb_pattern((0, 0, 30)))

    def button_pressed(self):
        if not self.audio.recording:
            self.set_recording()
            self.audio.start_recording()
            threading.Thread(target=self.handle_recording, daemon=True).start()

    def button_released(self):
        if self.audio.recording:
            self.audio.stop_recording()

    def handle_recording(self):
        try:
            # Record
            self.audio.record_audio(config.TEMP_AUDIO_FILE)
            
            # Speech recognition
            self.set_speech_recognition()
            text = self.speech.recognize_audio_file(config.TEMP_AUDIO_FILE)
            
            if text:
                # Claude thinking and speaking
                self.set_claude_thinking()
                answer = self.claude.ask_claude(text)
                
                # Speak while blue blinking continues
                self.audio.speak_text(answer)
            else:
                print("no speech recognized")
                self.audio.speak_text("not understood")
            
            # Cleanup
            if os.path.exists(config.TEMP_AUDIO_FILE):
                os.unlink(config.TEMP_AUDIO_FILE)
        
        except Exception as e:
            print(f"recording error: {e}")
        finally:
            # Back to ready
            self.set_ready()

    def run(self):
        try:
            print("Voice recorder running - press button to record")
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("stopping...")
        finally:
            self.leds.update(Leds.rgb_off())

def main():
    recorder = VoiceRecorder()
    recorder.run()

if __name__ == '__main__':
    main()
