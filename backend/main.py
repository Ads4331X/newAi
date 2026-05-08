import json
import sys
import os
import glob
import subprocess
import re
import urllib.request
import urllib.error
import system_commands
import power_commands
import memory
import tts_speak

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "conversation_history.json")
FAST_HISTORY_TURNS = 2
MAX_MEMORY_KEYS = 12
MAX_APPS_IN_PROMPT = 120

os.makedirs(os.path.dirname(history_path), exist_ok=True)
try:
    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
        if not isinstance(history, list):
            history = []
except Exception:
    history = []

powerComands = ["SHUTDOWN", "RESTART", "SUSPEND", "SLEEP", "LOGOUT", "LOCK", "REBOOT"]
_cached_apps_list = None
_cached_user_context = None


def _load_env_file(env_path):
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


def _init_env():
    root_env = os.path.join(os.path.dirname(BASE_DIR), ".env")
    backend_env = os.path.join(BASE_DIR, ".env")
    _load_env_file(root_env)
    _load_env_file(backend_env)


def openrouter_chat(messages):
    api_key = os.environ.get("OPEN_ROUTER_API_KEY", "").strip()
    model = os.environ.get("OPEN_ROUTER_AI_MODEL", "openai/gpt-oss-20b:free").strip()
    if not api_key:
        return "[SPEAK]OpenRouter API key is missing. Please set OPEN_ROUTER_API_KEY in .env."

    timeout_seconds = float(os.environ.get("OPEN_ROUTER_TIMEOUT", "12"))
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 180,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url="https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "newAi-assistant",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8")
        parsed = json.loads(body)
        choices = parsed.get("choices") or []
        if not choices:
            return "[SPEAK]OpenRouter returned no choices."

        message = choices[0].get("message") or {}
        content = message.get("content")

        if isinstance(content, str):
            text = content.strip()
            if text:
                return text

        # Some models return content as structured parts, or null when only
        # reasoning/tool fields are present.
        if isinstance(content, dict):
            text_val = content.get("text")
            if isinstance(text_val, str) and text_val.strip():
                return text_val.strip()

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict):
                    text_val = part.get("text")
                    if isinstance(text_val, str) and text_val.strip():
                        text_parts.append(text_val.strip())
                elif isinstance(part, str) and part.strip():
                    text_parts.append(part.strip())
            if text_parts:
                return "\n".join(text_parts).strip()

        # Additional compatibility fallbacks across providers.
        choice_text = choices[0].get("text")
        if isinstance(choice_text, str) and choice_text.strip():
            return choice_text.strip()

        delta_content = (choices[0].get("delta") or {}).get("content")
        if isinstance(delta_content, str) and delta_content.strip():
            return delta_content.strip()

        output_text = parsed.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        error_obj = parsed.get("error")
        if isinstance(error_obj, dict):
            message_text = error_obj.get("message")
            if isinstance(message_text, str) and message_text.strip():
                return f"[SPEAK]OpenRouter error: {message_text.strip()}"

        # Fallback to avoid crashing on null content responses.
        return "[SPEAK]I received an empty response from OpenRouter. Please try again."
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return f"[SPEAK]OpenRouter request failed with status {e.code}. {detail[:300]}"
    except Exception as e:
        return f"[SPEAK]OpenRouter request failed: {str(e)}"


_init_env()


def _collect_apps_once():
    global _cached_apps_list
    if _cached_apps_list is not None:
        return _cached_apps_list
    apps = []
    for desktop_file in glob.glob('/usr/share/applications/*.desktop'):
        try:
            name = ""
            exec_cmd = ""
            with open(desktop_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith('Name=') and not name:
                        name = line.split('=', 1)[1].strip()
                    if line.startswith('Exec=') and not exec_cmd:
                        exec_cmd = line.split('=', 1)[1].strip().split('%')[0].strip().split()[0]
            if name and exec_cmd:
                apps.append(f"{name} = {exec_cmd}")
        except Exception:
            continue
    _cached_apps_list = "\n".join(apps[:MAX_APPS_IN_PROMPT])
    return _cached_apps_list


def _get_user_context_once():
    global _cached_user_context
    if _cached_user_context is not None:
        return _cached_user_context

    try:
        username = os.environ.get("USER", "erza")
        home = os.path.expanduser("~")
        with open("/etc/os-release", "r", encoding="utf-8", errors="ignore") as f:
            os_release = f.read()
        distro = os_release.split("PRETTY_NAME=")[1].split("\n")[0].strip('"')
    except Exception:
        username, home, distro = "erza", "/home/erza", "Ubuntu"

    _cached_user_context = (username, home, distro)
    return _cached_user_context


def _compact_memory_for_prompt(mem):
    if not isinstance(mem, dict) or not mem:
        return "{}"
    compact = {}
    for idx, (key, value) in enumerate(mem.items()):
        if idx >= MAX_MEMORY_KEYS:
            break
        compact[key] = value
    return json.dumps(compact, separators=(",", ":"))


def build_system_prompt():
    mem = memory.get_memory()
    memory_str = _compact_memory_for_prompt(mem)
    username, home, distro = _get_user_context_once()

    apps_list = _collect_apps_once()

    return f"""You are Hatsune Miku, a fast AI assistant on {distro}.
User: {username}, Home: {home}

USER MEMORY (JSON):
{memory_str}

TOOLS YOU HAVE:
- [BASH] - run ANY bash command
- [SPEAK] - say something (max 1 sentence, no markdown)
- [MEMORY] - store important facts about user permanently
- notify-send - desktop notifications
- apt - install software

INSTALLED APPS (Name = binary):
{apps_list}

RULES:
1. Output only tags.
2. Keep replies brief.
3. One [BASH] command per line.
4. GUI apps must end with &.
5. Use [MEMORY] for important user facts/preferences.

FORMAT:
[SPEAK]text
[BASH]command
[MEMORY]{{"key": "value"}}

EXAMPLES:
user says "my name is Erza" →
[SPEAK]Nice to meet you Erza!
[MEMORY]{{"name": "Erza"}}

user says "I prefer dark mode" →
[SPEAK]Got it, I will remember that!
[MEMORY]{{"theme": "dark"}}

CORRECT BASH:
[BASH]google-chrome &
[BASH]filezilla &

WRONG BASH:
[BASH]chrome & filezilla &"""


def run_and_capture(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=8,
            env={
                **os.environ,
                'DISPLAY': os.environ.get('DISPLAY', ':1'),
                'DBUS_SESSION_BUS_ADDRESS': os.environ.get(
                    'DBUS_SESSION_BUS_ADDRESS',
                    'unix:path=/run/user/1000/bus'
                )
            }
        )
        return (result.stdout + result.stderr).strip()
    except Exception as e:
        return str(e)


def _extract_tag_content(chunk, tag):
    tag_upper = f"[{tag}]"
    chunk_strip = chunk.strip()
    upper = chunk_strip.upper()
    idx = upper.find(tag_upper)
    if idx != -1:
        return chunk_strip[idx + len(tag_upper):].strip()
    return ""


def _remove_memory_segments(text):
    # Remove inline memory directives from user-visible text.
    return re.sub(r"\[MEMORY\]\s*\{.*?\}", "", text, flags=re.IGNORECASE | re.DOTALL).strip()


def _strip_inline_json(text):
    decoder = json.JSONDecoder()
    i = 0
    out = []
    length = len(text)

    while i < length:
        ch = text[i]
        if ch in "{[":
            try:
                obj, end = decoder.raw_decode(text[i:])
                if isinstance(obj, (dict, list)):
                    # Skip parsed JSON fragment from user-visible output.
                    i += end
                    continue
            except Exception:
                pass
        out.append(ch)
        i += 1
    return "".join(out)


def _clean_user_visible_text(text):
    cleaned = _remove_memory_segments(text)
    cleaned = _strip_inline_json(cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


for line in sys.stdin:
    user_prompt = line.strip()

    if not user_prompt:
        continue

    # Always interrupt ongoing speech as soon as next prompt arrives.
    tts_speak.stop_speaking()

    if user_prompt.upper() in ["QUIT", "EXIT", "Q", "E"]:
        print("Exiting...", flush=True)
        break

    if user_prompt.upper() in powerComands:
        power_commands.power_commands(user_prompt.upper())
        print("Power command executed", flush=True)
        continue
    
    if user_prompt == "MIC_START":
        import stt_listen
        text = stt_listen.listen_and_transcribe()
        if text:
            print(f"STT:{text}", flush=True)
        continue
    if user_prompt == "STOP_SPEAKING":
        tts_speak.stop_speaking()
        continue

    recent_history = history[-FAST_HISTORY_TURNS:] if len(history) > FAST_HISTORY_TURNS else history

    messages = [
        {"role": "system", "content": build_system_prompt()},
        *recent_history,
        {"role": "user", "content": user_prompt},
    ]

    output = openrouter_chat(messages)
    output = output.replace("[NOTE]", "").replace("[SAFETY]", "").strip()
    output_user_visible = _clean_user_visible_text(output)

    speak_lines = []
    for chunk in output_user_visible.split("\n"):
        t = _extract_tag_content(chunk, "SPEAK")
        if t:
            t = _clean_user_visible_text(t)
            speak_lines.append(t)

    if speak_lines:
        print(" ".join(speak_lines), flush=True)

    normalized = output.replace("[BASH]", "\n[BASH]").replace("[SPEAK]", "\n[SPEAK]").replace("[MEMORY]", "\n[MEMORY]")
    bash_outputs = []

    for chunk in normalized.split("\n"):
        chunk = chunk.strip()
        if not chunk:
            continue

        chunk_upper = chunk.upper()

        if "[BASH]" in chunk_upper:
            if "[BASH]" in chunk:
                command = chunk.split("[BASH]")[1].strip()
            else:
                command = chunk.split("[bash]")[1].strip()

            command = command.replace("```", "").replace("`", "").strip()

            if command.endswith("&"):
                system_commands.system_commands(command)
            else:
                cmd_output = run_and_capture(command)
                if cmd_output:
                    bash_outputs.append(f"$ {command}\n{cmd_output}")

        elif "[MEMORY]" in chunk_upper:
            try:
                mem_str = _extract_tag_content(chunk, "MEMORY")
                mem_data = json.loads(mem_str)
                memory.update_memory(mem_data)
            except Exception as e:
                print(f"MEMORY ERROR: {e}", flush=True)

        elif "[SPEAK]" in chunk_upper:
            text = _extract_tag_content(chunk, "SPEAK")
            if text:
                text = _clean_user_visible_text(text)
                if text:
                    tts_speak.tts_speak_async(text)

    if bash_outputs:
        combined = "\n".join(bash_outputs)
        print(f"BASH OUTPUT: {combined}", flush=True)
        summary_clean = "Command finished. I have shown the output on screen."
        print(summary_clean, flush=True)
        tts_speak.tts_speak_async(summary_clean)

        output = output + f"\n[BASH OUTPUT]: {combined}"

    if not any(tag in output.upper() for tag in ["[BASH]", "[SPEAK]"]):
        clean_output = _clean_user_visible_text(output_user_visible)
        if clean_output:
            tts_speak.tts_speak_async(clean_output)
            print(clean_output, flush=True)

    # Save only user-facing assistant text to history (no [MEMORY]/[BASH] tags).
    assistant_history_text = " ".join(speak_lines).strip()
    if not assistant_history_text:
        assistant_history_text = re.sub(r"\[(SPEAK|MEMORY|BASH)\]", "", output_user_visible, flags=re.IGNORECASE).strip()

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': assistant_history_text})

    if len(history) > 8:
        history = history[-8:]

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)