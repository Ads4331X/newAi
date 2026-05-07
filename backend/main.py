from ollama import chat, ChatResponse
import json
import sys
import os
import glob
import subprocess
import re
import system_commands
import power_commands
import memory
import tts_speak

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "conversation_history.json")

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
    _cached_apps_list = "\n".join(apps)
    return _cached_apps_list


def build_system_prompt():
    mem = memory.get_memory()
    memory_str = json.dumps(mem, indent=2) if mem else "No memories yet"

    try:
        username = os.environ.get('USER', 'erza')
        home = os.path.expanduser('~')
        with open('/etc/os-release', "r", encoding="utf-8", errors="ignore") as f:
            os_release = f.read()
        distro = os_release.split('PRETTY_NAME=')[1].split('\n')[0].strip('"')
    except Exception:
        username, home, distro = 'erza', '/home/erza', 'Ubuntu'

    apps_list = _collect_apps_once()

    return f"""You are Hatsune Miku, AI assistant on {distro}.
User: {username}, Home: {home}

WHAT YOU KNOW ABOUT THE USER:
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
1. NEVER write plain text outside tags
2. EACH command gets its OWN [BASH] tag on its OWN line
3. GUI apps MUST end with &
4. BE BRIEF!
5. ALWAYS use [MEMORY] when user tells you their name or preferences

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
            timeout=10,
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

    recent_history = history[-4:] if len(history) > 4 else history

    messages = [
        {"role": "system", "content": build_system_prompt()},
        *recent_history,
        {"role": "user", "content": user_prompt},
    ]

    response: ChatResponse = chat(model='gemma3:4b', messages=messages)
    output = response.message.content.strip()
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