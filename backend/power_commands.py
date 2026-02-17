import subprocess

def power_commands(command):
    commands = {
        "SHUTDOWN": "shutdown now",
        "RESTART": "reboot",
        "REBOOT": "reboot",
        "SUSPEND": "systemctl suspend",
        "SLEEP": "systemctl suspend",
        "LOGOUT": "gnome-session-quit --logout --no-prompt",
        "LOCK": "gnome-screensaver-command -l"
    }
    
    if command in commands:
        subprocess.run(commands[command], shell=True)