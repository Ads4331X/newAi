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

_stop_event = threading.Event()
_aplay_process = None
_speak_queue = queue.Queue()
_worker_thread = None
_worker_lock = threading.Lock()

def stop_speaking():
    global _aplay_process
    _stop_event.set()
    if _aplay_process:
        try:
            _aplay_process.terminate()
        except Exception:
            pass

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

def _tts_speak_blocking(text):
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

def _speak_worker():
    while True:
        text = _speak_queue.get()
        if text is None:
            _speak_queue.task_done()
            continue
        _stop_event.clear()
        _tts_speak_blocking(text)
        _speak_queue.task_done()

def _ensure_worker():
    global _worker_thread
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_thread = threading.Thread(target=_speak_worker, daemon=True)
            _worker_thread.start()

def tts_speak(text):
    _stop_event.clear()
    _tts_speak_blocking(text)

def tts_speak_async(text):
    stop_speaking()
    _ensure_worker()
    # Drop stale queued messages so only latest response is spoken.
    while True:
        try:
            _speak_queue.get_nowait()
            _speak_queue.task_done()
        except queue.Empty:
            break
    _speak_queue.put(text)