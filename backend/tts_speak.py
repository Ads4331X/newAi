import warnings
import logging
import sys
import os

# Completely silence TTS
os.environ['TTS_LOG_LEVEL'] = 'ERROR'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)

# Redirect stdout temporarily during TTS init
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

from TTS.api import TTS
import subprocess
import time
import re

tts_engine = TTS("tts_models/en/ljspeech/vits")

sys.stdout.close()
sys.stdout = old_stdout

def tts_speak(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            audio_file = f'/tmp/voice_{int(time.time())}.wav'
            
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            tts_engine.tts_to_file(text=sentence, file_path=audio_file)
            
            sys.stdout.close()
            sys.stdout = old_stdout
            
            subprocess.run(['aplay', '-q', audio_file], check=False)
            try:
                os.remove(audio_file) 
            except:
                pass