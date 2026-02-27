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

    recent_history = history[-4:] if len(history) > 4 else history

    messages = [
        *recent_history,
        {"role": "user", "content": user_prompt},
    {
    "role": "system",
    "content": """You are Hatsune Miku, Ubuntu assistant.

CRITICAL RULES:
1. Be EXTREMELY brief - 1-2 sentences maximum!
2. ALWAYS use UPPERCASE tags: [BASH] or [SPEAK]
3. Use markdown formatting in [SPEAK] responses:
   - **bold** for emphasis
   - *italic* for tone
   - `code` for commands/file names
   - - lists when needed
4. For long explanations, use text WITHOUT [SPEAK] tag.


FORMAT:
[BASH]command
[SPEAK]formatted text with **bold**, *italic*, `code`

FORMATTING EXAMPLES:
"what is freedom" → [SPEAK]Freedom is **doing what you want** while *respecting others*.
"how to install vlc" → [SPEAK]Use: `sudo apt install vlc -y`
"what's important" → [SPEAK]**Privacy** and *security* are key!
"list features" → [SPEAK]Features: **Fast**, *Reliable*, Easy to use

COMMAND EXAMPLES:
"open chrome" → [BASH]google-chrome &
"hello" → [SPEAK]Hi! I'm **Miku**!
"install vlc" → [BASH]sudo apt install vlc -y

RULES:
- Use **bold** for important words
- Use *italic* for emphasis/tone
- Use `backticks` for commands
- Max 2 sentences for [SPEAK]!
- Add & for GUI apps
- BE BRIEF!"""
}]

    response: ChatResponse = chat(model='qwen2.5:1.5b', messages=messages)
    output = response.message.content.strip()

    # Remove formatting garbage
    # output = output.replace("**", "").replace("[BOLD]", "").replace("[/BOLD]", "")
    output = output.replace("[NOTE]", "").replace("[SAFETY]", "").strip()

    # Clean display
    display_output = output.replace("[BASH]", "").replace("[SPEAK]", "").strip()
    print(f"{display_output}", flush=True)

    for line in output.split("\n"):
        line = line.strip()
        if not line or line.startswith("[") and "]" not in line:
            continue

        line_upper = line.upper()

        if "[BASH]" in line_upper:
            if "[BASH]" in line:
                command = line.split("[BASH]")[1].strip()
            else:
                command = line.split("[bash]")[1].strip()
            
            command = command.replace("```","").replace("`","").strip()
            if command:
                system_commands.system_commands(command)
                time.sleep(0.1)

        elif "[SPEAK]" in line_upper:
            if "[SPEAK]" in line:
                command = line.split("[SPEAK]")[1].strip()
            else:
                command = line.split("[speak]")[1].strip()
            
            if command:
                tts_speak.tts_speak(command)

    if not any(tag in output.upper() for tag in ["[BASH]", "[SPEAK]"]):
        tts_speak.tts_speak(output)

    history.append({'role': 'user', 'content': user_prompt})
    history.append({'role': 'assistant', 'content': output})

    # Keep only last 8 messages
    if len(history) > 8:
        history = history[-8:]

    with open(history_path, "w") as data:
        json.dump(history, data)