from ollama import chat, ChatResponse
import json
import sys
import os
import time
import glob
import subprocess
import system_commands
import power_commands
import tts_speak

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "conversation_history.json")

with open(history_path, "r") as data:
    history = json.load(data)

powerComands = ["SHUTDOWN", "RESTART", "SUSPEND", "SLEEP", "LOGOUT", "LOCK", "REBOOT"]


def build_system_prompt():
    try:
        apps = []
        for f in glob.glob('/usr/share/applications/*.desktop'):
            try:
                name = ""
                exec_cmd = ""
                for line in open(f).readlines():
                    if line.startswith('Name=') and not name:
                        name = line.split('=', 1)[1].strip()
                    if line.startswith('Exec=') and not exec_cmd:
                        exec_cmd = line.split('=', 1)[1].strip().split('%')[0].strip().split()[0]
                if name and exec_cmd:
                    apps.append(f"{name} = {exec_cmd}")
            except:
                continue
        apps_list = "\n".join(apps)
    except:
        apps_list = ""

    try:
        username = os.environ.get('USER', 'erza')
        home = os.path.expanduser('~')
        distro = open('/etc/os-release').read().split('PRETTY_NAME=')[1].split('\n')[0].strip('"')
    except:
        username, home, distro = 'erza', '/home/erza', 'Ubuntu'

    return f"""You are Hatsune Miku, AI assistant on {distro}.
User: {username}, Home: {home}

TOOLS YOU HAVE:
- [BASH] - run ANY bash command
- [SPEAK] - say something (max 1 sentence, no markdown)
- notify-send - desktop notifications
- apt - install software

INSTALLED APPS (Name = binary):
{apps_list}

RULES:
1. NEVER write plain text outside tags
2. EACH command gets its OWN [BASH] tag on its OWN line
3. GUI apps MUST end with &
4. BE BRIEF!

CORRECT:
[BASH]google-chrome &
[BASH]filezilla &
[BASH]gnome-calculator &

WRONG (never do this):
[BASH]chrome & filezilla & calculator

FORMAT:
[SPEAK]text
[BASH]command"""


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


for line in sys.stdin:
    user_prompt = line.strip()

    if not user_prompt:
        continue

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

    recent_history = history[-4:] if len(history) > 4 else history

    messages = [
        {"role": "system", "content": build_system_prompt()},
        *recent_history,
        {"role": "user", "content": user_prompt},
    ]

    response: ChatResponse = chat(model='gemma3:4b', messages=messages)
    output = response.message.content.strip()
    output = output.replace("[NOTE]", "").replace("[SAFETY]", "").strip()

    display_output = output.replace("[BASH]", "").replace("[SPEAK]", "").strip()
    print(f"{display_output}", flush=True)

    normalized = output.replace("[BASH]", "\n[BASH]").replace("[SPEAK]", "\n[SPEAK]")

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
                time.sleep(0.5)
            else:
                cmd_output = run_and_capture(command)
                if cmd_output:
                    bash_outputs.append(f"$ {command}\n{cmd_output}")
                time.sleep(0.2)

        elif "[SPEAK]" in chunk_upper:
            if "[SPEAK]" in chunk:
                text = chunk.split("[SPEAK]")[1].strip()
            else:
                text = chunk.split("[speak]")[1].strip()
            if text:
                tts_speak.stop_speaking()
                tts_speak.tts_speak(text)

    if bash_outputs:
        combined = "\n".join(bash_outputs)
        print(f"BASH OUTPUT: {combined}", flush=True)

        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": f"Command output:\n{combined}\nBriefly summarize in [SPEAK]."})

        summary_resp = chat(model='gemma3:4b', messages=messages)
        summary = summary_resp.message.content.strip()
        summary_clean = summary.replace("[SPEAK]", "").replace("[BASH]", "").strip()
        print(f"{summary_clean}", flush=True)
        tts_speak.stop_speaking()
        tts_speak.tts_speak(summary_clean)

        output = output + f"\n[BASH OUTPUT]: {combined}"

    if not any(tag in output.upper() for tag in ["[BASH]", "[SPEAK]"]):
        tts_speak.stop_speaking()
        tts_speak.tts_speak(output)

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': output})

    if len(history) > 8:
        history = history[-8:]

    with open(history_path, "w") as data:
        json.dump(history, data, indent=2)