import subprocess
import os
import glob

def find_app(name):
    """Try to find the real binary for an app name"""
    # 1. Try direct command
    result = subprocess.run(['which', name], capture_output=True, text=True)
    if result.returncode == 0:
        return name
    
    # 2. Search .desktop files for matching app
    desktop_dirs = [
        '/usr/share/applications/',
        os.path.expanduser('~/.local/share/applications/')
    ]
    name_lower = name.lower()
    for d in desktop_dirs:
        for f in glob.glob(d + '*.desktop'):
            try:
                content = open(f).read().lower()
                if name_lower in content:
                    for line in open(f).readlines():
                        if line.startswith('Exec='):
                            cmd = line.split('=', 1)[1].strip()
                            cmd = cmd.split('%')[0].strip()
                            return cmd
            except:
                continue
    return None

def system_commands(command):
    original = command.strip()
    
    # If it looks like a simple app launch (ends with & or is a single word)
    is_app_launch = original.endswith('&') or (len(original.split()) == 1)
    
    if is_app_launch:
        # Extract the app name (first word, strip &)
        app_name = original.replace('&', '').strip().split()[0]
        found = find_app(app_name)
        if found:
            command = found + ' &'
    
    try:
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ, 'DISPLAY': ':0'}
        )
    except Exception as e:
        print(f"Error running command: {e}", flush=True)