import sqlite3
import webbrowser
import urllib.parse
import time
import pyautogui

# Connect to database
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute("SELECT phone, message FROM whatsapp_messages")
rows = cursor.fetchall()
conn.close()

# Loop through each record and open WhatsApp Web
for phone, msg in rows:
    phone = phone.replace("+", "").replace(" ", "")
    encoded_msg = urllib.parse.quote(msg)
    url = f"https://wa.me/{phone}?text={encoded_msg}"

    print(f"Opening: {url}")
    webbrowser.open(url)         # ✅ Only opens once
    time.sleep(10)               # Wait for WhatsApp Web to load
    pyautogui.press('enter')     # Send message
    time.sleep(5)                # Small delay before next
