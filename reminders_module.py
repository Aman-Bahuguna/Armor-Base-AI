import json
import os
import time
import threading
import datetime
import dateparser
import ollama
import pyttsx3
import config

class RemindersAssistant:
    def __init__(self):
        self.reminders_file = config.REMINDERS_DB
        self.shopping_file = config.SHOPPING_DB
        self.todo_file = config.TODO_DB
        
        # Load Data
        self.reminders = self.load_data(self.reminders_file)
        self.shopping_list = self.load_data(self.shopping_file)
        self.todo_list = self.load_data(self.todo_file)
        
        # TTS Engine for background alerts
        self.engine = None 
        
        # Start Background Scheduler
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    # --- STORAGE ---
    def load_data(self, filepath):
        if not os.path.exists(filepath): return []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except: return []

    def save_data(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    # --- CORE FUNCTIONS ---
    def add_reminder(self, title, time_str, category="General", recurring=None):
        dt = dateparser.parse(time_str)
        if not dt:
            # Try parsing relative time manually or fallback
            dt = datetime.datetime.now() # Fallback to now if parse fails (user should edit)
        
        reminder = {
            "id": int(time.time()),
            "title": title,
            "time": dt.isoformat(),
            "category": category,
            "recurring": recurring,
            "status": "pending"
        }
        self.reminders.append(reminder)
        self.save_data(self.reminders_file, self.reminders)
        return f"Reminder set for {dt.strftime('%A, %d %b at %I:%M %p')}."

    def add_todo(self, item, priority="Medium"):
        task = {
            "id": int(time.time()),
            "item": item,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        self.todo_list.append(task)
        self.save_data(self.todo_file, self.todo_list)
        return f"Added '{item}' to To-Do list."

    def add_shopping(self, item, quantity="1"):
        entry = {
            "id": int(time.time()),
            "item": item,
            "quantity": quantity,
            "status": "pending"
        }
        self.shopping_list.append(entry)
        self.save_data(self.shopping_file, self.shopping_list)
        return f"Added '{item}' to Shopping list."

    def delete_item(self, db_type, item_id):
        if db_type == "reminder":
            self.reminders = [x for x in self.reminders if x['id'] != item_id]
            self.save_data(self.reminders_file, self.reminders)
        elif db_type == "todo":
            self.todo_list = [x for x in self.todo_list if x['id'] != item_id]
            self.save_data(self.todo_file, self.todo_list)
        elif db_type == "shopping":
            self.shopping_list = [x for x in self.shopping_list if x['id'] != item_id]
            self.save_data(self.shopping_file, self.shopping_list)

    def toggle_status(self, db_type, item_id):
        target_list = None
        file_path = None
        
        if db_type == "todo":
            target_list = self.todo_list
            file_path = self.todo_file
        elif db_type == "shopping":
            target_list = self.shopping_list
            file_path = self.shopping_file
            
        if target_list is not None:
            for x in target_list:
                if x['id'] == item_id:
                    x['status'] = 'completed' if x['status'] == 'pending' else 'pending'
            self.save_data(file_path, target_list)

    # --- LLM PARSING ---
    def parse_command(self, text):
        """Uses Ollama to determine if it's a reminder, todo, or shopping item."""
        try:
            prompt = f"""
            Analyze command: "{text}"
            
            Determine intent: "reminder", "todo", "shopping".
            
            Return JSON:
            {{
                "intent": "reminder" | "todo" | "shopping",
                "content": "task name or item name",
                "time": "natural language time (e.g. tomorrow 5pm)" (only for reminder, else null),
                "category": "work/personal/home" (optional),
                "recurring": "daily/weekly" (if mentioned, else null)
            }}
            
            Return ONLY JSON.
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start, end = content.find('{'), content.rfind('}') + 1
            if start != -1:
                return json.loads(content[start:end])
            return None
        except Exception as e:
            print(f"Parsing Error: {e}")
            return None

    # --- BACKGROUND WORKER ---
    def _speak_alert(self, text):
        """Thread-safe TTS trigger"""
        try:
            # Re-init engine inside thread to avoid conflicts
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            pass

    def _scheduler_loop(self):
        """Checks for due reminders every 10 seconds."""
        while self.running:
            now = datetime.datetime.now()
            dirty = False
            
            for r in self.reminders:
                if r['status'] == 'pending':
                    rem_time = datetime.datetime.fromisoformat(r['time'])
                    # Trigger if time matches within the last minute
                    if rem_time <= now:
                        # 1. Speak
                        self._speak_alert(f"Reminder: {r['title']}")
                        
                        # 2. Update Status
                        r['status'] = 'triggered'
                        
                        # 3. Handle Recurrence
                        if r.get('recurring') == 'daily':
                            new_time = rem_time + datetime.timedelta(days=1)
                            r['time'] = new_time.isoformat()
                            r['status'] = 'pending'
                        elif r.get('recurring') == 'weekly':
                            new_time = rem_time + datetime.timedelta(weeks=1)
                            r['time'] = new_time.isoformat()
                            r['status'] = 'pending'
                            
                        dirty = True
            
            if dirty:
                self.save_data(self.reminders_file, self.reminders)
                
            time.sleep(10)