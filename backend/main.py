from ollama import chat, ChatResponse
import json
import sys
import os
import time
# import pyttsx3
import system_commands
import power_commands
import tts_speak

# engine = pyttsx3.init()
# engine.setProperty('rate', 150)
# engine.setProperty('volume', 1.0)
# voices = engine.getProperty('voices')
# if len(voices) > 1:
#     engine.setProperty('voice', voices[1].id)
# else:
#     engine.setProperty('voice', voices[0].id)

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

    recent_history = history[-6:] if len(history) > 6 else history

    messages = [
        *recent_history,
        {"role": "user", "content": user_prompt},
        {
            "role": "system",
            "content": """You are Hatsune Miku, an Ubuntu Linux AI assistant with FULL system access.

You can do ANYTHING on Ubuntu by generating bash commands.

RESPONSE FORMAT - each on its own line:
[BASH]command     → run any bash command
[SPEAK]text       → say something to user

THAT'S IT. Only 2 tags needed for everything!

EXAMPLES:
"open chrome" → [BASH]google-chrome
"open terminal" → [BASH]gnome-terminal
"open calculator" → [BASH]gnome-calculator
"open files" → [BASH]nautilus
"open files in downloads" → [BASH]nautilus ~/Downloads
"open youtube" → [BASH]google-chrome https://youtube.com
"open gmail" → [BASH]google-chrome https://gmail.com
"open vscode" → [BASH]code
"open system monitor" → [BASH]gnome-system-monitor
"open settings" → [BASH]gnome-control-center
"install vlc" → [BASH]sudo apt install vlc -y
"update system" → [BASH]sudo apt update && sudo apt upgrade -y
"make folder test" → [BASH]mkdir ~/test
"make folder test in downloads" → [BASH]mkdir ~/Downloads/test
"delete folder test" → [BASH]rm -rf ~/test
"calculate sin(45)" → [BASH]python3 -c "import math; print(math.sin(math.radians(45)))"
"calculate 2+2" → [BASH]python3 -c "print(2+2)"
"what is my ip" → [BASH]hostname -I
"show disk space" → [BASH]df -h
"create python file helloworld" → [BASH]echo "print('Hello, World!')" > ~/hello.py
"hello" → [SPEAK]Hello! I am Miku, your Ubuntu assistant!
"how to install vlc" → [SPEAK]Run sudo apt install vlc -y in your terminal!
"minimize current window" → [BASH]xdotool getactivewindow windowminimize
"close current window" → [BASH]xdotool getactivewindow windowclose
"maximize current window" → [BASH]xdotool getactivewindow windowmaximize
"change tab" -> [BASh] command to change tab
RULES:
- Use [BASH] for ALL system actions including opening apps
- Use [SPEAK] only for chat or explanations
- NO other tags needed
- NO markdown, NO backticks
- ONE command per line
- Apps need & to run in background: google-chrome &
- NEVER add & to bash file/folder commands"""
        }
    ]

    response: ChatResponse = chat(model='gemma3:4b', messages=messages)
    output = response.message.content.strip()

    print(f"AI: {output}", flush=True)

    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue

        if "[BASH]" in line:
            command = line.split("[BASH]")[1].strip()
            command = command.replace("```","").replace("`","").strip()
            if command:
                print(f"RUNNING: {command}", flush=True)
                system_commands.system_commands(command)
                time.sleep(0.3)

        elif "[SPEAK]" in line:
            command = line.split("[SPEAK]")[1].strip()
            if command:
                print(f"SPEAKING: {command}", flush=True)
                tts_speak.tts_speak(command)

    if not any(tag in output for tag in ["[BASH]", "[SPEAK]"]):
        print(f"AI: {output}", flush=True)
        tts_speak.tts_speak(output)

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': output})

    with open(history_path, "w") as data:
        json.dump(history, data)