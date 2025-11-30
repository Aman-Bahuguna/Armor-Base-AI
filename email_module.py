import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import config
import ollama
from bs4 import BeautifulSoup
import re

class EmailAssistant:
    def __init__(self):
        self.sender_email = config.EMAIL_SENDER_ADDRESS
        self.password = config.EMAIL_APP_PASSWORD
        self.contacts_file = config.CONTACTS_FILE
        self.contacts = self.load_contacts()

    # --- CONTACT MANAGEMENT ---
    def load_contacts(self):
        if not os.path.exists(self.contacts_file):
            return []
        try:
            with open(self.contacts_file, 'r') as f:
                data = json.load(f)
                return data.get("contacts", [])
        except Exception as e:
            print(f"Error loading contacts: {e}")
            return []

    def save_contacts(self):
        with open(self.contacts_file, 'w') as f:
            json.dump({"contacts": self.contacts}, f, indent=4)

    def add_contact(self, name, email_addr):
        for c in self.contacts:
            if c['name'].lower() == name.lower():
                c['email'] = email_addr
                self.save_contacts()
                return f"Updated contact {name}."
        
        self.contacts.append({"name": name.lower(), "email": email_addr})
        self.save_contacts()
        return f"Added new contact {name}."

    def get_email_from_name(self, name):
        name = name.lower().strip()
        for contact in self.contacts:
            if contact['name'] in name or name in contact['name']:
                return contact['email']
        return None

    # --- AI GENERATION & PARSING ---
    def generate_email_body(self, subject, recipient_name="Recipient"):
        """Generates a full email body based on the subject using local AI."""
        try:
            prompt = f"""
            Write a professional and concise email body.
            Subject: "{subject}"
            To: {recipient_name}
            From: Me
            
            Return ONLY the body text. Do not include subject lines or placeholders like [Your Name].
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content'].strip()
        except Exception as e:
            return f"Error generating email: {str(e)}"

    def parse_voice_command(self, text):
        try:
            prompt = f"""
            You are an API that converts email commands into JSON.
            Contacts: {[c['name'] for c in self.contacts]}
            Command: "{text}"
            
            Extract: 'recipient_name', 'recipient_email', 'subject', 'body'.
            If the user only mentions a topic but no body, leave body null.
            Return ONLY valid JSON.
            """
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1:
                return json.loads(content[start:end])
            return None
        except Exception:
            return None

    # --- SENDING ---
    def validate_email(self, email_addr):
        # Basic regex for email validation
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email_addr) is not None

    def send_email(self, recipient_email, subject, body):
        # 1. Validate Email Format (Allows sending to "anyone")
        recipient_email = recipient_email.strip()
        if not self.validate_email(recipient_email):
            return False, f"Invalid email address format: {recipient_email}"

        if not self.sender_email or not self.password:
            return False, "Email config missing."

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
            server.login(self.sender_email, self.password)
            server.send_message(msg)
            server.quit()
            return True, f"Email sent to {recipient_email}."
        except Exception as e:
            return False, f"Failed to send: {str(e)}"

    # --- READING ---
    def fetch_recent_emails(self, limit=5):
        if not self.sender_email or not self.password: return []
        try:
            mail = imaplib.IMAP4_SSL(config.IMAP_SERVER)
            mail.login(self.sender_email, self.password)
            mail.select("inbox")
            status, messages = mail.search(None, "ALL")
            latest_ids = messages[0].split()[-limit:]
            email_list = []
            for eid in reversed(latest_ids):
                res, msg_data = mail.fetch(eid, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subj = email.header.decode_header(msg["Subject"])[0][0]
                        if isinstance(subj, bytes): subj = subj.decode()
                        sender = msg.get("From")
                        email_list.append({"sender": sender, "subject": subj, "preview": "Email content hidden for privacy."})
            mail.close()
            mail.logout()
            return email_list
        except Exception as e:
            print(f"IMAP Error: {e}")
            return []