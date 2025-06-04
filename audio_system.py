import subprocess
import time
import os
import config

# AIY Audio imports
import sys
sys.path.insert(0, config.PYTHON_PATH)
from aiy.voice.audio import AudioFormat, record_file, FilePlayer

class AudioSystem:
    def __init__(self):
        self.recording = False
        self.audio_format = AudioFormat(
            sample_rate_hz=config.SAMPLE_RATE,
            num_channels=1,
            bytes_per_sample=2
        )
        
    def record_audio(self, output_file):

        try:
            print("starting AIY recording...")
            
            def wait_for_stop():
                while self.recording:
                    time.sleep(0.1)
                print("recording stopped")
            
            # AIY record_file
            record_file(self.audio_format, output_file, 'wav', wait_for_stop)
            
            # Check result
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"audio recorded: {size} bytes")
                return size > 1000
            else:
                print("audio file not created")
                return False
            
        except Exception as e:
            print(f"audio recording error: {e}")
            return False

    def speak_text(self, text):
        try:
            
            data = "<volume level='60'><pitch level='130'><speed level='100'>%s</speed></pitch></volume>" % text
            subprocess.run(['pico2wave', '-w', '/tmp/tts.wav', '-l', 'de-DE', data])
            player = FilePlayer()
            player.play_wav('/tmp/tts.wav', device='default')
            player.join()
            os.unlink('/tmp/tts.wav')
            return True
            
        except Exception as e:
            print(f"TTS error: {e}")
            return False
             
    def start_recording(self):
        """Start recording mode"""
        self.recording = True
    
    def stop_recording(self):
        """Stop recording mode"""
        self.recording = False
