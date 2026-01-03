import os
import asyncio
import sounddevice as sd
import numpy as np
import wave
import tempfile
from faster_whisper import WhisperModel
import edge_tts

class VoiceEngine:
    """
    Handles Speech-to-Text (Ear) and Text-to-Speech (Mouth).
    Optimized for NVIDIA GPU.
    """
    def __init__(self, model_size="medium", device="cuda"):
        print(f"Loading Whisper model ({model_size}) on {device}...")
        try:
            # compute_type="float16" is standard for 3050
            self.model = WhisperModel(model_size, device=device, compute_type="float16")
            print("Whisper model loaded.")
        except Exception as e:
            print(f"Failed to load Whisper on GPU: {e}. Falling back to CPU.")
            self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

        self.voice = "en-US-EricNeural" # A good male voice
        # self.voice = "en-US-AriaNeural" # A good female voice

    def listen(self, duration=5, samplerate=16000) -> str:
        """
         records audio for a fixed duration (simple version) and transcribes.
         TODO: Implement VAD for dynamic duration.
        """
        print("Listening...")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        print("Processing audio...")

        # Save to temp wav file (Whisper likes files or float arrays)
        # We can pass the numpy array directly to faster-whisper usually, 
        # but let's be safe and use a temp file for compatibility.
        # Actually faster_whisper decode accepts np array (float32).
        
        # Convert to float32 normalized
        audio_float = audio_data.flatten().astype(np.float32) / 32768.0
        
        segments, info = self.model.transcribe(audio_float, beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        print(f"Heard: {text}")
        return text.strip()

    def speak(self, text: str):
        """
        Uses Edge-TTS to speak the text.
        """
        print(f"Speaking: {text}")
        asyncio.run(self._speak_async(text))

    async def _speak_async(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        # We need to play audio. Edge-TTS saves to file or yields bytes.
        # Simplest: Save to temp file and play.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            
        await communicate.save(temp_path)
        
        # Play the file (using a simple Windows command or library)
        # os.system(f"start {temp_path}") # This opens player window, annoying.
        # Better: use pygame or playsound if available. 
        # Requirement said 'sounddevice' and 'pyaudio'. 
        # Let's try to decode mp3... tricky without ffmpeg.
        # Edge-TTS output is mp3. 
        # Workaround for '2-hour' constraint: Use powershell to play sound invisible
        
        self._play_audio_powershell(temp_path)
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass

    def _play_audio_powershell(self, file_path):
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
        except ImportError:
            print("Pygame not found. Using os.startfile")
            os.startfile(file_path)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def observe(self, action: dict, result, error: str = None) -> str:
        """
        Creates a textual observation from the action result.
        Required by CoreAgentController.
        """
        if error:
            return f"Action failed with error: {error}"
        
        if result is None:
            return "Action completed with no output."
        
        # Truncate long results
        result_str = str(result)
        if len(result_str) > 500:
            result_str = result_str[:500] + "... (truncated)"
        
        return f"Action completed. Result: {result_str}"

