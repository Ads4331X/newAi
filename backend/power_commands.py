import subprocess

def power_commands(command):
    commands = {
        "SHUTDOWN": ["shutdown", "now"],
        "RESTART": ["reboot"],
        "REBOOT": ["reboot"],
        "SUSPEND": ["systemctl", "suspend"],
        "SLEEP": ["systemctl", "suspend"],
        "LOGOUT": ["gnome-session-quit", "--logout", "--no-prompt"],
        "LOCK": ["loginctl", "lock-session"],
    }

    if command in commands:
        try:
            subprocess.run(commands[command], check=False, timeout=5)
        except Exception:
            pass