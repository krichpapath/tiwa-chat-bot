import keyboard
import speech_recognition as sr
from playsound import playsound
import os


class Tiwa_SpeechRecognizer:
    def __init__(self, language="th-TH"):
        self.recognizer = sr.Recognizer()
        self.language = language  # Language for speech recognition
        self.corrections = {
            "วิวาห์": "ทิวา",
            "ที่ว่า": "ทิวา",
            "พี่ว่า": "ทิวา",
            "ที่บ้าน": "ทิวา",
            "ชีวา": "ทิวา",
        }

    def record_audio(self):
        """Record audio from the microphone."""
        with sr.Microphone() as source:
            print("Recording...")
            playsound("Tiwa_sound/ฟังอยู่ค่ะ.wav")
            audio_data = self.recognizer.listen(source)
            print("Done...")
            playsound("Tiwa_sound/แปปนึงนะคะ.wav")
            return audio_data

    def transcribe_audio(self, audio_data):
        """Transcribe audio data to text."""
        try:
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            corrected_text = self.correct_transcription(text)
            return corrected_text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}"
            )

    def correct_transcription(self, text):
        """Correct specific transcription errors."""
        for incorrect, correct in self.corrections.items():
            text = text.replace(incorrect, correct)
        return text

    def transcribe_audio_file(self, file_path):
        """Transcribe audio from a file."""
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            corrected_text = self.correct_transcription(text)
            return corrected_text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}"
            )


if __name__ == "__main__":
    recognizer = Tiwa_SpeechRecognizer()
    # Example usage
    audio_data = recognizer.record_audio()
    print(f"Transcribe sentence is {recognizer.transcribe_audio(audio_data)}")
