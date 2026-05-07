import subprocess
import os

def system_commands(command):
    command = command.strip()
    print(f"EXECUTING: {command}", flush=True)
    
    try:
        env = os.environ.copy()
        env["HOME"] = env.get("HOME", "/home/erza")
        env["USER"] = env.get("USER", "erza")
        env["DISPLAY"] = env.get("DISPLAY", ":1")
        env["DBUS_SESSION_BUS_ADDRESS"] = env.get("DBUS_SESSION_BUS_ADDRESS", "unix:path=/run/user/1000/bus")
        env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", "/run/user/1000")
        env["PATH"] = env.get("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin")

        subprocess.Popen(
            command,
            shell=True,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error running command: {e}", flush=True)