from ollama import chat, ChatResponse
import json
import sys
import os
import system_commands 
import update_commands
import power_commands


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "conversation_history.json")
#read conversatoin_history.json file
with open(history_path, "r") as data:
  history = json.load(data)

powerComands = ["SHUTDOWN", "RESTART", "SUSPEND", "SLEEP", "LOGOUT", "LOCK", "REBOOT"]

for line in sys.stdin:
    user_prompt = line.strip().upper()
    
    if not user_prompt:
        continue
    
    # Check for exit
    if user_prompt in ["QUIT", "EXIT", "Q", "E"]:
        print("Exiting...", flush=True)
        break
    
    # Check for power commands
    if user_prompt in powerComands:
        power_commands.power_commands(user_prompt)
        print("Power command executed", flush=True)
        continue

    if user_prompt in powerComands:
      power_commands.power_commands(user_prompt)

    messages = [*history, {"role": "user", "content": user_prompt}]
    hasOpen = False  
    hasUpdate = False
    
    if "UPDATE" in user_prompt:   
      applicationName = " ".join(user_prompt.split()[user_prompt.split().index("UPDATE") + 1:])
      hasUpdate = True
      messages.append({"role": "system",  
                        "content": f"""Return the apt install command to update this app: {applicationName}                                 
                                      Examples:
                                      chrome/google → sudo apt update && sudo apt install --only-upgrade google-chrome-stable -y
                                      calculator → sudo apt update && sudo apt install --only-upgrade gnome-calculator -y
                                      system/all → sudo apt update && sudo apt upgrade -y
                                      Return command for: {applicationName}"""})
    
    elif "OPEN" in user_prompt:   
      applicationName = " ".join(user_prompt.split()[user_prompt.split().index("OPEN") + 1:])
      hasOpen = True
      messages.append({"role": "system",
                        "content": f"""CRITICAL INSTRUCTION: Return ONLY the executable command. NO explanations, NO questions, NO extra text.
                                    Ubuntu command mappings:
                                    chrome/google → google-chrome
                                    calculator → gnome-calculator
                                    files → nautilus
                                    terminal → gnome-terminal

                                    User request: {applicationName}

                                    Return format: Just the command name, nothing else.
                                    Example responses:
                                    google-chrome
                                    gnome-calculator
                                    nautilus

                                    Your response (command only):"""})
    else:
      messages.append(  {
    "role": "system",
    "content": "You are an Ubuntu assistant. Only give instructions relevant to Ubuntu/Linux. Ignore instructions about Windows or Mac. Explain step by step in simple language and proactively suggest what the user might need next."
  })
    
    response: ChatResponse = chat(model='qwen2.5:1.5b', messages=messages)  
    print(f"AI: {response.message.content}", flush=True)

    if hasOpen:  
      system_commands.system_commands(response.message.content)
      hasOpen = False

    if hasUpdate:  
      update_commands.update_commands(response.message.content)
      hasUpdate = False

    history.append({'role': 'user', 'content': user_prompt})  
    history.append({'role': 'assistant', 'content': response.message.content})
    
    with open(history_path , "w") as data:  
      json.dump(history, data)


