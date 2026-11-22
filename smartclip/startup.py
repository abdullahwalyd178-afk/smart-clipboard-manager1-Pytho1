import sys
KEY=r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
NAME="SmartClipboardManager"
def set_startup(enabled):
    if sys.platform!="win32": raise RuntimeError("Windows startup is only supported on Windows.")
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,KEY,0,winreg.KEY_SET_VALUE) as key:
        if enabled: winreg.SetValueEx(key,NAME,0,winreg.REG_SZ,f'"{sys.executable}" -m smartclip')
        else:
            try: winreg.DeleteValue(key,NAME)
            except FileNotFoundError: pass
