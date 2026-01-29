from ollama import chat, ChatResponse
import json
import system_commands 
import update_commands


#read conversatoin_history.json file
with open("backend/data/conversation_history.json" , "r") as data:
  history = json.load(data)

user_prompt = ""
hasOpen = False  
hasUpdate = False
exit = {
  "QUIT": True,
  "EXIT": True,
  "Q": True,
  "E": True,
}
def getResponse():
  global user_prompt
  global hasOpen
  global hasUpdate
  user_prompt = input("Enter a Prompt: ").upper()

  while user_prompt not in exit.keys() : 
    messages = [*history, {"role": "user", "content": user_prompt}]
    
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
    
    if "OPEN" in user_prompt:   
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
    
    response: ChatResponse = chat(model='qwen2.5:1.5b', messages=messages)  
    
    if hasOpen:  
      system_commands.system_commands(response.message.content)
      hasOpen = False

    if hasUpdate:  
      update_commands.update_commands(response.message.content)
      hasUpdate = False

    history.append({'role': 'user', 'content': user_prompt})  
    history.append({'role': 'assistant', 'content': response.message.content})
    
    with open("backend/data/conversation_history.json" , "w") as data:  
      json.dump(history, data)

    print("Enter Exit/Quit/E to exit\n")  
    user_prompt = input("Enter a Prompt: ").upper()  

getResponse()