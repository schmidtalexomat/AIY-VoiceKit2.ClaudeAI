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
from aiy.leds import Leds, Color
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
        self.blink_active = False
        
        # Ready - solid dim green
        self.leds.update(Leds.rgb_on((0, 10, 0)))
        self.audio.speak_text("yo")

    def blink_during_phase(self, color):
        """Start blinking for entire phase"""
        self.blink_active = True
        while self.blink_active:
            self.leds.update(Leds.rgb_on(color))
            time.sleep(0.3)
            if not self.blink_active:
                break
            self.leds.update(Leds.rgb_off())
            time.sleep(0.3)

    def stop_blinking(self):
        """Stop blinking"""
        self.blink_active = False

    def button_pressed(self):
        if not self.audio.recording:
            print("rec start")
            # Start red blinking for entire recording phase
            threading.Thread(target=self.blink_during_phase, args=((30, 0, 0),), daemon=True).start()
            self.audio.start_recording()
            threading.Thread(target=self.handle_recording, daemon=True).start()

    def button_released(self):
        if self.audio.recording:
            print("rec stop")
            self.audio.stop_recording()

    def handle_recording(self):
        try:
            # Record (red blinking continues from button_pressed)
            self.audio.record_audio(config.TEMP_AUDIO_FILE)
            
            # Switch to purple blinking for speech recognition
            self.stop_blinking()
            time.sleep(0.1)
            threading.Thread(target=self.blink_during_phase, args=((30, 0, 30),), daemon=True).start()
            print("processing speech...")
            text = self.speech.recognize_audio_file(config.TEMP_AUDIO_FILE)
            
            if text:
                # Switch to blue blinking for Claude
                self.stop_blinking()
                time.sleep(0.1)
                threading.Thread(target=self.blink_during_phase, args=((0, 0, 30),), daemon=True).start()
                answer = self.claude.ask_claude(text)
                
                # Stop blinking before speaking
                self.stop_blinking()
                
                # Speak Claude's answer
                self.audio.speak_text(answer)
            else:
                print("no speech recognized")
                self.stop_blinking()
                self.audio.speak_text("not understood")
            
            # Cleanup
            if os.path.exists(config.TEMP_AUDIO_FILE):
                os.unlink(config.TEMP_AUDIO_FILE)
        
        except Exception as e:
            print(f"recording error: {e}")
        finally:
            # Back to ready - solid dim green
            self.stop_blinking()
            time.sleep(0.2)
            self.leds.update(Leds.rgb_on((0, 10, 0)))

    def run(self):
        try:
            print("Voice recorder running - press button to record")
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("stopping...")
        finally:
            self.stop_blinking()
            self.leds.update(Leds.rgb_off())

def main():
    recorder = VoiceRecorder()
    recorder.run()

if __name__ == '__main__':
    main()
