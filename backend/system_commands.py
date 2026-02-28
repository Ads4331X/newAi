import subprocess
import os

def system_commands(command):
    command = command.strip()
    print(f"EXECUTING: {command}", flush=True)
    try:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={
                **os.environ,
                'DISPLAY': os.environ.get('DISPLAY', ':1'),
                'DBUS_SESSION_BUS_ADDRESS': os.environ.get(
                    'DBUS_SESSION_BUS_ADDRESS',
                    'unix:path=/run/user/1000/bus'
                )
            }
        )
    except Exception as e:
        print(f"Error running command: {e}", flush=True)