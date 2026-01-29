
import subprocess
import os
import time

def system_commands(res ):



    bash_file = open("openApplication_bash_script.sh" , "w")
    bash_file.write(res)
    bash_file.close()

    subprocess.run(["chmod", "+x", "openApplication_bash_script.sh"])
    subprocess.Popen(["bash", "openApplication_bash_script.sh"])
    print(res)

    time.sleep(0.5)  # Wait a moment for bash to start reading the file
    os.remove("openApplication_bash_script.sh")

   
