from ollama import chat, ChatResponse
import json
import system_commands 

#read conversatoin_history.json file
with open("backend/data/conversation_history.json" , "r") as data:
  history = json.load(data)
  
user_prompt = ""
hasOpen = False

exit = {
  "QUIT": True,
  "EXIT": True,
  "Q": True,
  "E": True,
}

def getResponse():
  user_prompt = input("Enter a Prompt: ").upper()

  while user_prompt not in exit.keys() : 
    messages = [*history, {"role": "user", "content": user_prompt}]  # FIXED: removed extra braces

    if "OPEN" in user_prompt:
       applicationName = " ".join(user_prompt.split()[user_prompt.split().index("OPEN") + 1:])
       hasOpen = True
       messages.append({"role": "system",   # FIXED: removed extra brackets
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
    
    # FIXED: proper indentation
    response: ChatResponse = chat(model='qwen2.5:1.5b', messages=messages)
    
    if hasOpen:
      system_commands.system_commands(response.message.content)
      hasOpen = False

    history.append({'role': 'user', 'content': user_prompt})  # FIXED: order (user first, then assistant)
    history.append({'role': 'assistant', 'content': response.message.content})
    
    with open("backend/data/conversation_history.json" , "w") as data:
      json.dump(history, data)

    print("Enter Exit/Quit/E to exit\n")
    user_prompt = input("Enter a Prompt: ").upper()

getResponse()