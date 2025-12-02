import cv2
import threading
import time
import json
import os
import datetime
import pyttsx3
import ollama
import config

class SecuritySystem:
    def __init__(self):
        self.active = False
        self.camera_index = 0
        self.lock = threading.Lock()
        
        # Config
        self.log_file = config.SECURITY_LOG_DB
        self.capture_dir = config.SECURITY_CAPTURES_DIR
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir)
            
        # State
        self.latest_frame = None
        self.last_motion_time = 0
        self.is_recording = False
        self.alert_cooldown = 0
        
        # Settings
        self.sensitivity = 5000  # Lower = more sensitive
        self.alert_tts = True
        self.alert_email = False
        self.alert_telegram = False
        
        # Dependencies (Injected later)
        self.email_bot = None
        self.msg_bot = None

    def load_logs(self):
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r') as f: return json.load(f)
        except: return []

    def log_event(self, event_type, filename):
        logs = self.load_logs()
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_type,
            "file": filename
        }
        logs.insert(0, entry)
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)

    def speak_alert(self, text):
        """Thread-safe TTS"""
        if not self.alert_tts: return
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except: pass

    def send_remote_alerts(self, msg):
        # Email
        if self.alert_email and self.email_bot:
            # We assume a default contact or configured admin email
            admin_email = config.EMAIL_SENDER_ADDRESS # Send to self
            self.email_bot.send_email(admin_email, "SECURITY ALERT", msg)
        
        # Telegram
        if self.alert_telegram and self.msg_bot and self.msg_bot.contacts:
            # Send to first contact with telegram_id as admin
            for c in self.msg_bot.contacts:
                if c.get('telegram_id'):
                    self.msg_bot.send_telegram(c['telegram_id'], f"🚨 {msg}")
                    break

    def start_surveillance(self):
        if self.active: return "Security Protocol already active."
        self.active = True
        self.thread = threading.Thread(target=self._surveillance_loop, daemon=True)
        self.thread.start()
        return "Security Protocol Initiated. Monitoring webcam."

    def stop_surveillance(self):
        self.active = False
        return "Security Protocol Deactivated."

    def _surveillance_loop(self):
        cap = cv2.VideoCapture(self.camera_index)
        
        # Baseline frame for motion
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()
        
        while self.active and cap.isOpened():
            # 1. Processing
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) < self.sensitivity:
                    continue
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 0, 255), 2)

            # 2. Update shared frame for UI
            with self.lock:
                self.latest_frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)

            # 3. Alert Logic
            if motion_detected:
                now = time.time()
                if now - self.alert_cooldown > 10: # 10 sec cooldown
                    self.alert_cooldown = now
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Alert
                    self.speak_alert("Motion detected in secure sector.")
                    self.send_remote_alerts(f"Motion detected at {timestamp}")
                    
                    # Save Evidence
                    filename = f"capture_{timestamp}.jpg"
                    filepath = os.path.join(self.capture_dir, filename)
                    cv2.imwrite(filepath, frame1)
                    self.log_event("Motion Detected", filename)

            # 4. Cycle Frames
            frame1 = frame2
            ret, frame2 = cap.read()
            if not ret: break
            
            # CPU Optimization sleep
            time.sleep(0.05)

        cap.release()
        self.active = False

    # --- LLM Parsing ---
    def parse_security_command(self, text):
        try:
            prompt = f"""
            Analyze security command: "{text}"
            Return JSON: {{
                "intent": "activate" | "deactivate" | "show_log" | "settings",
                "setting_key": "sensitivity" | "email_alert" (optional),
                "setting_value": "high/low" | "on/off" (optional)
            }}
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start, end = content.find('{'), content.rfind('}') + 1
            return json.loads(content[start:end])
        except: return None