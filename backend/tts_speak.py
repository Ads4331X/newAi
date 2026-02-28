import re
import queue
import threading
import subprocess
import os
import tempfile
import soundfile as sf
from kokoro_onnx import Kokoro

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kokoro = Kokoro(
    os.path.join(BASE_DIR, "voices", "kokoro-v1.0.onnx"), 
    os.path.join(BASE_DIR, "voices", "voices-v1.0.bin")
)
VOICE = "af_bella"

# Global stop flag
_stop_event = threading.Event()
_aplay_process = None

def stop_speaking():
    global _aplay_process
    _stop_event.set()
    if _aplay_process:
        _aplay_process.terminate()

def clean_text(text):
    text = text.replace("**", "").replace("*", "").replace("`", "").replace("#", "")
    return text.strip()

def split_chunks(text):
    chunks = re.split(r'(?<=[.!?,]) +', text)
    return [c.strip() for c in chunks if c.strip()]

def generate_chunk(text):
    samples, sample_rate = kokoro.create(text, voice=VOICE, speed=1.0, lang="en-us")
    return samples, sample_rate

def player_worker(play_queue):
    global _aplay_process
    while True:
        item = play_queue.get()
        if item is None:
            break
        if _stop_event.is_set():
            play_queue.task_done()
            continue
        path = item[0]
        _aplay_process = subprocess.Popen(['aplay', '-q', path])
        _aplay_process.wait()
        _aplay_process = None
        try:
            os.remove(path)
        except:
            pass
        play_queue.task_done()

def tts_speak(text):
    global _stop_event
    # Reset stop flag for new speech
    _stop_event.clear()

    text = clean_text(text)
    if not text:
        return
    chunks = split_chunks(text)
    if not chunks:
        return
    play_queue = queue.Queue()
    player_thread = threading.Thread(target=player_worker, args=(play_queue,), daemon=True)
    player_thread.start()
    for chunk in chunks:
        if _stop_event.is_set():
            break
        samples, sample_rate = generate_chunk(chunk)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        sf.write(tmp.name, samples, sample_rate)
        play_queue.put((tmp.name,))
    play_queue.put(None)
    player_thread.join()