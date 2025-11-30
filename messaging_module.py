import json
import os
import time
import threading
import datetime
import asyncio
import webbrowser
import pyautogui
import urllib.parse
import config
import ollama
import dateparser
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters

class MessagingAssistant:
    def __init__(self):
        self.contacts_file = config.CONTACTS_FILE
        self.scheduled_file = config.SCHEDULED_DB
        self.contacts = self.load_contacts()
        self.scheduled_messages = self.load_scheduled()
        self.incoming_log = [] 
        self.auto_reply_history = []
        
        # Flags
        self.sentiment_analysis_enabled = True
        self.global_auto_reply = False
        
        self.running = True
        
        # 1. Scheduler Thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # 2. Telegram Bot Thread
        if config.TELEGRAM_BOT_TOKEN and "YOUR_" not in config.TELEGRAM_BOT_TOKEN:
            self.telegram_thread = threading.Thread(target=self._run_telegram_bot, daemon=True)
            self.telegram_thread.start()

    # --- DATA MANAGEMENT ---
    def load_contacts(self):
        if not os.path.exists(self.contacts_file): return []
        try:
            with open(self.contacts_file, 'r') as f:
                return json.load(f).get("contacts", [])
        except: return []

    def save_contacts(self):
        with open(self.contacts_file, 'w') as f:
            json.dump({"contacts": self.contacts}, f, indent=4)

    def load_scheduled(self):
        if not os.path.exists(self.scheduled_file): return []
        try:
            with open(self.scheduled_file, 'r') as f:
                return json.load(f)
        except: return []

    def save_scheduled(self):
        with open(self.scheduled_file, 'w') as f:
            json.dump(self.scheduled_messages, f, indent=4)

    def get_contact(self, name):
        name = name.lower()
        for c in self.contacts:
            if c['name'].lower() in name:
                return c
        return None

    # --- LLM INTELLIGENCE ---
    def parse_command(self, text):
        try:
            prompt = f"""
            Extract messaging details from command: "{text}".
            Contacts: {[c['name'] for c in self.contacts]}
            
            Return JSON with keys:
            - intent: "send" or "schedule"
            - platform: "whatsapp", "telegram" or null
            - recipient_name: name found or null
            - message_body: content to send
            - schedule_time: if scheduling, natural text (e.g. "tomorrow 9am"), else null
            
            Return ONLY JSON.
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start, end = content.find('{'), content.rfind('}') + 1
            if start != -1:
                data = json.loads(content[start:end])
                if data.get('schedule_time'):
                    dt = dateparser.parse(data['schedule_time'])
                    if dt: data['schedule_time'] = dt.isoformat()
                return data
            return None
        except Exception as e:
            print(f"Parsing error: {e}")
            return None

    def analyze_sentiment(self, text):
        if not self.sentiment_analysis_enabled:
            return {"sentiment": "neutral", "emotion": "neutral"}
        try:
            prompt = f"""
            Analyze sentiment of: "{text}".
            Return JSON: {{ "sentiment": "positive"|"neutral"|"negative", "emotion": "one_word_label" }}
            ONLY JSON.
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start, end = content.find('{'), content.rfind('}') + 1
            return json.loads(content[start:end])
        except:
            return {"sentiment": "neutral", "emotion": "unknown"}

    def generate_reply(self, original_text, emotion):
        try:
            prompt = f"""
            Write a short, helpful text message reply to: "{original_text}".
            The sender is feeling {emotion}.
            Return ONLY the reply text.
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content'].strip().replace('"', '')
        except:
            return "Received."

    # --- MESSAGING ACTIONS ---
    def send_whatsapp(self, phone, message):
        """Uses Desktop App via URI Scheme + PyAutoGUI."""
        try:
            # 1. Clean phone number (remove +, spaces) if needed, but WhatsApp URI usually likes clean international format
            # ensure phone has no special chars except +
            
            # 2. Encode message
            encoded_msg = urllib.parse.quote(message)
            
            # 3. Construct URL
            # This URI scheme triggers the desktop app if installed
            url = f"whatsapp://send?phone={phone}&text={encoded_msg}"
            
            # 4. Open App
            webbrowser.open(url)
            
            # 5. Wait for App to Load (adjust sleep based on PC speed)
            time.sleep(4) 
            
            # 6. Press Enter to Send
            pyautogui.press('enter')
            
            return True, "Launched WhatsApp Desktop. Sent."
        except Exception as e:
            return False, f"WhatsApp Desktop Error: {e}"

    def send_telegram(self, chat_id, message):
        if not config.TELEGRAM_BOT_TOKEN:
            return False, "Telegram Token missing."
        
        async def _send():
            bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=chat_id, text=message)
        
        try:
            asyncio.run(_send())
            return True, "Telegram message sent."
        except Exception as e:
            return False, f"Telegram Error: {e}"

    def schedule_message(self, platform, recipient_data, message, time_iso):
        self.scheduled_messages.append({
            "id": int(time.time()),
            "platform": platform,
            "recipient": recipient_data,
            "message": message,
            "time": time_iso,
            "status": "pending"
        })
        self.save_scheduled()
        return True, f"Scheduled for {time_iso}"

    # --- BACKGROUND TASKS ---
    def _scheduler_loop(self):
        while self.running:
            now = datetime.datetime.now()
            for msg in self.scheduled_messages:
                if msg['status'] == 'pending':
                    sched_time = datetime.datetime.fromisoformat(msg['time'])
                    if now >= sched_time:
                        if msg['platform'] == 'whatsapp':
                            self.send_whatsapp(msg['recipient']['phone'], msg['message'])
                        elif msg['platform'] == 'telegram':
                            self.send_telegram(msg['recipient']['telegram_id'], msg['message'])
                        
                        msg['status'] = 'sent'
                        self.save_scheduled()
            time.sleep(60)

    def _run_telegram_bot(self):
        async def handle_msg(update, context):
            text = update.message.text
            sender_id = str(update.message.chat_id)
            sender_name = update.message.chat.first_name
            
            analysis = self.analyze_sentiment(text)
            reply = self.generate_reply(text, analysis['emotion'])
            
            log_entry = {
                "platform": "telegram",
                "sender": sender_name,
                "id": sender_id,
                "text": text,
                "analysis": analysis,
                "suggested_reply": reply,
                "time": datetime.datetime.now().strftime("%H:%M")
            }
            self.incoming_log.insert(0, log_entry)
            
            contact = None
            for c in self.contacts:
                if c.get('telegram_id') == sender_id:
                    contact = c
                    break
            
            should_reply = self.global_auto_reply
            if contact and 'auto_reply' in contact:
                should_reply = contact['auto_reply']
                
            if should_reply:
                await update.message.reply_text(reply)
                self.auto_reply_history.insert(0, {
                    "contact": sender_name,
                    "sentiment": analysis['emotion'],
                    "reply": reply,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })

        try:
            app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
            app.run_polling()
        except Exception as e:
            print(f"Bot Polling Error: {e}")