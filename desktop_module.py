import os
import json
import subprocess
import time
import psutil
import pyautogui
import ollama
import screen_brightness_control as sbc
from datetime import datetime

# Audio Control (Windows)
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class DesktopAssistant:
    def __init__(self, config_file="apps_config.json"):
        self.config_file = config_file
        self.apps = self.load_config()
        self.activity_log = []
        
        # Init Audio
        self.volume_interface = None
        if AUDIO_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            except:
                pass

    # --- CONFIG ---
    def load_config(self):
        if not os.path.exists(self.config_file):
            return []
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f).get("apps", [])
        except: return []

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({"apps": self.apps}, f, indent=4)

    def log_action(self, action, target, status="Success"):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": action,
            "target": target,
            "status": status
        }
        self.activity_log.insert(0, entry) # Prepend
        return f"{action}: {target} ({status})"

    # --- APP CONTROL ---
    def find_app(self, query):
        query = query.lower()
        for app in self.apps:
            if app['name'].lower() == query or query in app['aliases']:
                return app
        return None

    def open_app(self, app_name):
        app = self.find_app(app_name)
        if not app:
            return False, f"App '{app_name}' not configured."
        
        try:
            # Use Popen to not block the thread
            subprocess.Popen(app['path'])
            self.log_action("Open", app['name'])
            return True, f"Opening {app['name']}..."
        except Exception as e:
            self.log_action("Open", app['name'], f"Failed: {e}")
            return False, f"Error opening {app['name']}."

    def close_app(self, app_name):
        app = self.find_app(app_name)
        target_process = app['process_name'] if app else app_name 
        # If app is found in config use mapped process name, else try closing by name provided
        
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if target_process.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed:
            self.log_action("Close", app_name)
            return True, f"Closed {app_name}."
        else:
            return False, f"Process '{app_name}' not found running."

    # --- SYSTEM CONTROL ---
    def take_screenshot(self):
        folder = "screenshots"
        if not os.path.exists(folder): os.makedirs(folder)
        filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(folder, filename)
        try:
            pyautogui.screenshot(path)
            self.log_action("Screenshot", filename)
            return True, f"Saved to {path}"
        except Exception as e:
            return False, str(e)

    def set_volume(self, level):
        """Level 0-100"""
        if not self.volume_interface: return False, "Audio control unavailable."
        try:
            # Pycaw scalar is 0.0 to 1.0
            val = max(0.0, min(1.0, level / 100.0))
            self.volume_interface.SetMasterVolumeLevelScalar(val, None)
            return True, f"Volume set to {level}%"
        except Exception as e:
            return False, str(e)

    def change_volume(self, delta):
        if not self.volume_interface: return False, "Audio unavailable"
        try:
            current = self.volume_interface.GetMasterVolumeLevelScalar()
            new_val = max(0.0, min(1.0, current + (delta / 100.0)))
            self.volume_interface.SetMasterVolumeLevelScalar(new_val, None)
            return True, f"Volume changed."
        except: return False, "Error"

    def set_brightness(self, level):
        try:
            sbc.set_brightness(level)
            return True, f"Brightness set to {level}%"
        except Exception as e:
            return False, f"Brightness Error: {e}"

    def lock_computer(self):
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            self.log_action("System", "Lock Screen")
            return True, "Locking system."
        except:
            return False, "Lock failed (Windows only)."

    # --- LLM PARSING ---
    def parse_desktop_command(self, text):
        try:
            prompt = f"""
            Analyze desktop command: "{text}"
            Configured Apps: {[a['name'] for a in self.apps]}
            
            Return JSON with:
            - intent: open_app, close_app, screenshot, set_volume, set_brightness, lock_screen, type_text, scroll
            - target: app name (for open/close) or null
            - value: integer (for vol/brightness/scroll) or text (for type) or null
            
            Example: "Open Chrome" -> {{"intent": "open_app", "target": "Chrome"}}
            Example: "Volume 50" -> {{"intent": "set_volume", "value": 50}}
            """
            
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start, end = content.find('{'), content.rfind('}') + 1
            if start != -1:
                return json.loads(content[start:end])
            return None
        except Exception as e:
            print(f"Parsing error: {e}")
            return None