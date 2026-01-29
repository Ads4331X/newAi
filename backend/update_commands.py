
import subprocess
import os
import time

def update_commands(res ):



    bash_file = open("update_bash_script.sh" , "w")
    bash_file.write(res)
    bash_file.close()

    subprocess.run(["chmod", "+x", "update_bash_script.sh"])
    subprocess.run(["bash", "update_bash_script.sh"])
    print(res)

    time.sleep(0.5)  # Wait a moment for bash to start reading the file
    os.remove("update_bash_script.sh")

   
