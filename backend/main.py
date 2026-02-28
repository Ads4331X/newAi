from ollama import chat, ChatResponse
import json
import sys
import os
import time
import system_commands
import power_commands
import tts_speak

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "conversation_history.json")

with open(history_path, "r") as data:
    history = json.load(data)

powerComands = ["SHUTDOWN", "RESTART", "SUSPEND", "SLEEP", "LOGOUT", "LOCK", "REBOOT"]

SYSTEM_PROMPT = """You are Hatsune Miku, Ubuntu assistant.

CRITICAL RULES:
1. Be EXTREMELY brief - 1-2 sentences maximum!
2. ALWAYS use UPPERCASE tags: [BASH] or [SPEAK]
3. For multiple apps/commands, use ONE [BASH] tag per command on SEPARATE LINES.
4. No markdown in [SPEAK] - plain text only!

FORMAT:
[BASH]command
[SPEAK]plain text

COMMAND EXAMPLES:
"open chrome" → [BASH]google-chrome &
"hello" → [SPEAK]Hi! I am Miku!
"install vlc" → [BASH]sudo apt install vlc -y
"open chrome and files" →
[BASH]google-chrome &
[BASH]nautilus &
"open files" → [BASH]nautilus &
"open system monitor" → [BASH]gnome-system-monitor &
"open calculator" → [BASH]gnome-calculator &
"open filezilla" → [BASH]filezilla &
"open app center" → [BASH]snap-store &
"open any app" → [BASH]appname &
"open any unknown app" → [BASH]xdg-open appname &
"open a pdf" → [BASH]xdg-open /path/to/file.pdf &
"open folder" → [BASH]xdg-open /path/to/folder &
"update system" → [BASH]sudo apt update && sudo apt upgrade -y
"what time is it" → [BASH]notify-send "Time" "$(date +%H:%M)"
"whats the date" → [BASH]notify-send "Date" "$(date +%A, %B %d %Y)"
"disk space" → [BASH]notify-send "Disk Space" "$(df -h / | tail -1)"
"battery" → [BASH]notify-send "Battery" "$(cat /sys/class/power_supply/BAT0/capacity)%"
"screenshot" → [BASH]gnome-screenshot &
"volume up" → [BASH]pactl set-sink-volume @DEFAULT_SINK@ +10%
"volume down" → [BASH]pactl set-sink-volume @DEFAULT_SINK@ -10%
"mute" → [BASH]pactl set-sink-mute @DEFAULT_SINK@ toggle
"wifi on" → [BASH]nmcli radio wifi on
"wifi off" → [BASH]nmcli radio wifi off
"night light on" → [BASH]gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true
"night light off" → [BASH]gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled false
"bluetooth on" → [BASH]rfkill unblock bluetooth
"bluetooth off" → [BASH]rfkill block bluetooth
"empty trash" → [BASH]rm -rf ~/.local/share/Trash/*

RULES:
- One command per [BASH] tag
- Each [BASH] on its own line
- Add & for GUI apps
- Use xdg-open for any file or unknown app
- Use notify-send for info that should be read not spoken
- BE BRIEF!"""


def run_and_capture(command):
    """Run command and return output"""
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


def summarize_output(output_text, messages):
    """Ask LLM to summarize bash output"""
    follow_up = messages + [
        {"role": "assistant", "content": f"[BASH ran, output below]"},
        {"role": "user", "content": f"Command output: {output_text}\nSummarize this briefly in one sentence using [SPEAK]."}
    ]
    resp = chat(model='gemma3:4b', messages=follow_up)
    return resp.message.content.strip()


import subprocess

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
        {"role": "system", "content": SYSTEM_PROMPT},
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

            # GUI apps (end with &) - just launch, don't capture
            if command.endswith("&"):
                system_commands.system_commands(command)
                time.sleep(0.5)
            else:
                # Non-GUI commands - capture output
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

    # If there was bash output, let LLM summarize and speak it
    if bash_outputs:
        combined = "\n".join(bash_outputs)
        print(f"BASH OUTPUT: {combined}", flush=True)
        summary = summarize_output(combined, messages)
        summary_clean = summary.replace("[SPEAK]", "").replace("[BASH]", "").strip()
        print(f"{summary_clean}", flush=True)
        tts_speak.stop_speaking()
        tts_speak.tts_speak(summary_clean)

    if not any(tag in output.upper() for tag in ["[BASH]", "[SPEAK]"]):
        tts_speak.stop_speaking()
        tts_speak.tts_speak(output)

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': output})

    if len(history) > 8:
        history = history[-8:]

    with open(history_path, "w") as data:
        json.dump(history, data, indent=2)