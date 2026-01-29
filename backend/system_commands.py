
from ollama import chat , ChatResponse
import subprocess
import json
import os
import time

def system_commands(res ):

    # read the json file
    with open("backend/data/system_commands.json" , "r") as data:
        system_commands = json.load(data)

    bash_file = open("bash_script.sh" , "w")
    bash_file.write(res)
    bash_file.close()

    subprocess.run(["chmod", "+x", "bash_script.sh"])
    subprocess.Popen(["bash", "bash_script.sh"])
    print(res)



    time.sleep(0.5)  # Wait a moment for bash to start reading the file
    os.remove("bash_script.sh")



   
