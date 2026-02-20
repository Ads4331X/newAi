from TTS.api import TTS
import subprocess
import os
import time
import re
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("TTS").setLevel(logging.ERROR)

tts_engine = TTS("tts_models/en/ljspeech/tacotron2-DDC")

def tts_speak(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            audio_file = f'/tmp/voice_{int(time.time())}.wav'
            tts_engine.tts_to_file(text=sentence, file_path=audio_file)
            subprocess.run(['aplay', '-q', audio_file], check=False)
            try:
                os.remove(audio_file) 
            except:
                pass