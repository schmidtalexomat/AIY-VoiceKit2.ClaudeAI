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
        self.led_blink_active = False
        
        # Ready - dimmed green
        self.set_ready_led()
        self.audio.speak_text("yo")

    def set_ready_led(self):
        """Set dimmed green LED for ready state"""
        # Dimmed green (RGB values 0-255)
        self.leds.update(Leds.rgb_on((0, 10, 0)))

    def blink_led(self, color, duration=0.5, cycles=3):
        """Blink LED with specified color"""
        self.led_blink_active = True
        for _ in range(cycles):
            if not self.led_blink_active:
                break
            self.leds.update(Leds.rgb_on(color))
            time.sleep(duration / 2)
            self.leds.update(Leds.rgb_off())
            time.sleep(duration / 2)
        self.led_blink_active = False

    def button_pressed(self):
        if not self.audio.recording:
            print("rec start")
            # Red blinking during recording
            threading.Thread(target=self.blink_led, args=(Color.RED, 0.3, 999), daemon=True).start()
            self.audio.start_recording()
            threading.Thread(target=self.handle_recording, daemon=True).start()

    def button_released(self):
        if self.audio.recording:
            print("rec stop")
            self.led_blink_active = False  # Stop red blinking
            self.audio.stop_recording()

    def handle_recording(self):
        try:
            # Record
            self.audio.record_audio(config.TEMP_AUDIO_FILE)
            
            # Speech recognition - purple blinking
            threading.Thread(target=self.blink_led, args=(Color.PURPLE, 0.4, 5), daemon=True).start()
            print("processing speech...")
            text = self.speech.recognize_audio_file(config.TEMP_AUDIO_FILE)
            
            if text:
                # Blue blinking while Claude thinks
                self.led_blink_active = False  # Stop purple blinking
                time.sleep(0.2)  # Brief pause
                threading.Thread(target=self.blink_led, args=(Color.BLUE, 0.6, 999), daemon=True).start()
                
                answer = self.claude.ask_claude(text)
                
                # Stop blue blinking before speaking
                self.led_blink_active = False
                time.sleep(0.2)
                
                # Speak Claude's answer
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
            # Stop any blinking and back to ready
            self.led_blink_active = False
            time.sleep(0.3)
            self.set_ready_led()

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
