import subprocess
import shutil

def system_commands(applicationName):
    appCommands = {
        "CHROME": "google-chrome",
        "FILES": "nautilus",
        "VSCODE": "code",
        "TERMINAL": "gnome-terminal",
        "BASH": "gnome-terminal",
        "FILEMANAGER": "nautilus",
        "FILE": "nautilus"
        
    }
    if applicationName in appCommands:
        subprocess.Popen([appCommands[applicationName]])
    else:
        dir = shutil.which(applicationName)
        if(dir):
            subprocess.Popen([dir])
        else: 
            print("Application not found")



