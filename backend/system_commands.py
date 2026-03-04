import subprocess
import os

def system_commands(command):
    command = command.strip()
    print(f"EXECUTING: {command}", flush=True)
    
    try:
        # Launch via bash with clean environment
        subprocess.Popen(
            ['bash', '-c', f'env -i HOME=/home/erza USER=erza DISPLAY=:1 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin {command}'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error running command: {e}", flush=True)