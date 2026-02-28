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
        {
            "role": "system",
           "content": """You are Hatsune Miku, Ubuntu assistant.

CRITICAL RULES:
1. Be EXTREMELY brief - 1-2 sentences maximum!
2. ALWAYS use UPPERCASE tags: [BASH] or [SPEAK]
3. For multiple apps/commands, use ONE [BASH] tag per command on separate lines.
4. No markdown in [SPEAK] - plain text only!

FORMAT:
[BASH]command
[SPEAK]plain text

COMMAND EXAMPLES:
"open chrome" → [BASH]google-chrome &
"hello" → [SPEAK]Hi! I am Miku!
"install vlc" → [BASH]sudo apt install vlc -y
"open chrome and files" → [BASH]google-chrome &
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
- Add & for GUI apps
- Use xdg-open for any file or unknown app
- Use notify-send for info that should be read not spoken
- BE BRIEF!"""
        },
        *recent_history,
        {"role": "user", "content": user_prompt},
    ]

    response: ChatResponse = chat(model='qwen2.5:1.5b', messages=messages)
    output = response.message.content.strip()

    output = output.replace("[NOTE]", "").replace("[SAFETY]", "").strip()

    display_output = output.replace("[BASH]", "").replace("[SPEAK]", "").strip()
    print(f"{display_output}", flush=True)

    for chunk in output.split("\n"):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("[") and "]" not in chunk:
            continue

        chunk_upper = chunk.upper()

        if "[BASH]" in chunk_upper:
            if "[BASH]" in chunk:
                command = chunk.split("[BASH]")[1].strip()
            else:
                command = chunk.split("[bash]")[1].strip()

            command = command.replace("```", "").replace("`", "").strip()
            # Split on && or ; and run each separately
            for cmd in command.replace(";", "&&").split("&&"):
                cmd = cmd.strip()
                if cmd:
                    system_commands.system_commands(cmd)
                    time.sleep(0.2)

        elif "[SPEAK]" in chunk_upper:
            if "[SPEAK]" in chunk:
                text = chunk.split("[SPEAK]")[1].strip()
            else:
                text = chunk.split("[speak]")[1].strip()

            if text:
                tts_speak.tts_speak(text)

    if not any(tag in output.upper() for tag in ["[BASH]", "[SPEAK]"]):
        tts_speak.tts_speak(output)

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': output})

    if len(history) > 8:
        history = history[-8:]

    with open(history_path, "w") as data:
        json.dump(history, data)