import numpy as np
import sounddevice as sd
import tempfile
import wave
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
SAMPLE_RATE = 16000

def record_until_silence():
    chunks = []
    silence_count = 0
    started = False
    SILENCE_THRESHOLD = 0.012
    SILENCE_DURATION = 1.0
    MAX_RECORD = SAMPLE_RATE * 10
    total_samples = 0

    print("Listening... speak now!", flush=True)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        while True:
            chunk, _ = stream.read(1024)
            volume = np.abs(chunk).mean()
            total_samples += len(chunk)

            if volume > SILENCE_THRESHOLD:
                started = True
                silence_count = 0
                chunks.append(chunk)
            elif started:
                chunks.append(chunk)
                silence_count += len(chunk)
                if silence_count >= SAMPLE_RATE * SILENCE_DURATION:
                    break

            if total_samples >= MAX_RECORD:
                break

    if not chunks:
        return None

    audio = np.concatenate(chunks)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        return f.name

def listen_and_transcribe():
    path = record_until_silence()
    if not path:
        return ""
    segments, _ = model.transcribe(path, language="en")
    result = " ".join(s.text for s in segments).strip()
    return result