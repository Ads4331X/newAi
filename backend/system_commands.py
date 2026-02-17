import subprocess
import os
import time

def system_commands(res):
    res = res.strip()
    print(res, flush=True)
    
    timestamp = str(time.time()).replace(".", "")
    bash_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"launch_{timestamp}.sh"
    )
    
    with open(bash_path, "w") as bash_file:
        bash_file.write("#!/bin/bash\n")
        bash_file.write("export DISPLAY=:1\n")
        bash_file.write("export XAUTHORITY=$HOME/.Xauthority\n")
        bash_file.write(f"{res}\n")
        bash_file.write(f"rm -f {bash_path}\n")
    
    subprocess.run(["chmod", "+x", bash_path])
    subprocess.Popen(["bash", bash_path])
    time.sleep(0.2)
    print(f"Launched: {res}", flush=True)