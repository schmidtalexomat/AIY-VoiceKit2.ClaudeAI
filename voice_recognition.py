import speech_recognition as sr
import os

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        print("speech recognition ready")
    
    def recognize_audio_file(self, audio_file):
        """Recognize speech from WAV file - simple approach"""
        if not os.path.exists(audio_file):
            print(f"audio file not found: {audio_file}")
            return None
            
        try:
            print("recognizing speech...")
            
            # Load audio file
            with sr.AudioFile(audio_file) as source:
                # Noise reduction
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio_data = self.recognizer.record(source)
            
            # Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio_data, language='de-DE')
                return text.strip() if text.strip() else None
            except Exception as e:
                print(f"Google Speech not available: {e}")
                return None
            
        except Exception as e:
            print(f"speech recognition error: {e}")
            return None
