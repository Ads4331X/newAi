from ollama import chat, ChatResponse
import json
import system_commands 

#read conversatoin_history.json file
with open("backend/data/conversation_history.json" , "r") as data:
  history = json.load(data)
  
user_prompt = ""


exit = {
  "QUIT": True,
  "EXIT": True,
  "Q": True,
  "E": True,

}

def getResponse():
  user_prompt = input("Enter a Prompt: ").upper()


  while user_prompt not in exit.keys() : #loop till user doesnt give exit/quit/q
    if "OPEN" in user_prompt:
       applicationName =  user_prompt.split()[user_prompt.split().index("OPEN" ) + 1]
       system_commands.system_commands(applicationName) # opens an applications / performs system commands
    response: ChatResponse = chat(model='gemma3:1b', messages=[ #creates a model and response of user prompt
      *history,
      {
        'role': 'user',
        'content': user_prompt,
      },
    ])

    # append to the conevrsation_history 
    history.append({'role': 'assistant', 'content': response.message.content})
    history.append({'role': 'user', 'content': user_prompt})
    with open("backend/data/conversation_history.json" , "w") as data:
      json.dump(history, data)


      #print result
    print(response.message.content)
    print("Enter Exit/Quit/E to exit\n")
    user_prompt = input("Enter a Prompt: ").upper()



getResponse()




