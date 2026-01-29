import subprocess


def power_commands(command):
    powerCommands = {
        "SHUTDOWN": "poweroff",
        "Restart": "reboot",
        "Suspend": "systemctl suspend",
         "SLEEP": "systemctl suspend",
        "LOGOUT": "gnome-session-quit --logout",
        "LOCK": "gnome-screensaver-command -l",
        "REBOOT": "reboot",
    }

    cmd = powerCommands.get(command.upper())  # .get() returns None if not found
    if cmd:
        subprocess.run(cmd, shell=True)  # shell=True for commands with spaces
    else:
        print(f"Unknown power command: {command}")
