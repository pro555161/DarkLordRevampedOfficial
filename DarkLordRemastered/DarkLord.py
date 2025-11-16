import os
import sys
os.system("pip install -r src/requirements.txt")
from time import *
import os
import random
import string
import requests
import json
from datetime import datetime
from shutil import get_terminal_size
from rgbprint import rgbprint, gradient_print, gradient_scroll, Color
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings("ignore")

# ----------------------
# File Setup
# ----------------------
FILES_DIR = os.path.join(os.getcwd(), "files")
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

FILES = {
    "valid_tokens": os.path.join(FILES_DIR, "valid_tokens.json"),
    "invalid_tokens": os.path.join(FILES_DIR, "invalid_tokens.json"),
    "webhook_rename_history": os.path.join(FILES_DIR, "webhook_rename_history.json"),
    "webhook_spammer_history": os.path.join(FILES_DIR, "webhook_spammer_history.json"),
    "webhook_edit_image_history": os.path.join(FILES_DIR, "webhook_edit_image_history.json"),
    "webhook_delete_history": os.path.join(FILES_DIR, "webhook_delete_history.json"),
}

# Create files if missing
for path in FILES.values():
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")  # empty JSON array

# ----------------------
# Terminal helpers
# ----------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def init():
    os.system("title DarkLord Remastered - Webhook Tool")

# ----------------------
# Banner / Menu
# ----------------------
def banner():
    clear_console()
    ascii_art = [
        "                   _____     ______     ______     __  __        __         ______     ______     _____",
        "                 /\\  __-.  /\\  __ \\   /\\  == \\   /\\ \\/ /       /\\ \\       /\\  __ \\   /\\  == \\   /\\  __-.",
        "                 \\ \\ \\/\\ \\ \\ \\  __ \\  \\ \\  __<   \\ \\  _\"-.     \\ \\ \\____  \\ \\ \\/\\ \\  \\ \\  __<   \\ \\ \\/\\ \\",
        "                  \\ \\____-  \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_\\ \\_\\     \\ \\_____\\  \\ \\_____\\  \\ \\_\\ \\_\\  \\ \\____-",
        "                   \\/____/   \\/_/\\/_/   \\/_/\\/_/   \\/_/\\/_/      \\/_____/   \\/_____/   \\/_/\\/_/   \\/____/"
    ]
    for line in ascii_art:
        gradient_print(line, start_color=Color.purple, end_color=Color.medium_purple)

    menu = [
        "                   ┌───[1] Webhook Sender──┐  ┌───[2] Webhook Spammer──┐  ┌──[3] Webhook Deleter───┐",
        "                   └───────────────────────┘  └────────────────────────┘  └────────────────────────┘",
        "                     ┌───[4] Webhook Info──┐  ┌───[5] Token Generator──┐  ┌───[6] Rename Webhook──┐",
        "                     └─────────────────────┘  └────────────────────────┘  └───────────────────────┘",
        "                                     ┌──[7] Edit Webhook Image──┐  ┌───[0] Exit──┐",
        "                                     └──────────────────────────┘  └─────────────┘"
    ]
    for line in menu:
        gradient_print(line, start_color=Color.cyan, end_color=Color.blue)

# ----------------------
# Wavy Messages
# ----------------------
def wavy_message(text, color_start=Color.green, color_end=Color.cyan):
    gradient_scroll(text, start_color=color_start, end_color=color_end, delay=0.045, times=1)

# ----------------------
# File Helpers
# ----------------------
def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def validate_webhook(url):
    try:
        r = requests.get(url)
        return r.status_code == 200
    except:
        return False

def send_webhook_message():
    webhook = input("\nEnter the webhook URL: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    message = input("Enter the message: ")
    gradient_print("Sending message...", start_color=Color.cyan, end_color=Color.blue)
    try:
        requests.post(webhook, json={"content": message})
        gradient_print("Sending message...", start_color=Color.green_yellow, end_color=Color.blue)
        logs = read_json(FILES["webhook_spammer_history"])
        logs.append({"webhook": webhook, "message": message, "timestamp": str(datetime.utcnow())})
        write_json(FILES["webhook_spammer_history"], logs)
    except Exception as e:
        wavy_message(f"Error: {e}", Color.red, Color.red)
    input("\nPress Enter to continue...")
    
def spam_webhook():
    webhook = input("\nEnter webhook URL: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    message = input("Message to spam: ")
    try:
        amount = int(input("How many messages?: "))
    except ValueError:
        wavy_message("[ERROR] Invalid input.", Color.red, Color.red)
        return
    wavy_message(f"Sending all {amount} messages...", Color.cyan, Color.blue)
    for i in range(1, amount + 1):
        try:
            requests.post(webhook, json={"content": message})
            gradient_print("Sent.", start_color=Color.cyan, end_color=Color.blue)
        except Exception as e:
            wavy_message(f"Error: {e}", Color.red, Color.red)
            break
    logs = read_json(FILES["webhook_spammer_history"])
    logs.append({"webhook": webhook, "message": message, "amount": amount, "timestamp": str(datetime.utcnow())})
    write_json(FILES["webhook_spammer_history"], logs)
    wavy_message("All messages sent.", Color.cyan, Color.blue)
    input("\nPress Enter to continue...")

def delete_webhook():
    webhook = input("\nEnter webhook URL to delete: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    wavy_message("Attempting to delete webhook...", Color.cyan, Color.blue)
    try:
        response = requests.delete(webhook)
        if response.status_code == 204:
            wavy_message("Webhook deleted.", Color.green, Color.light_green)
        else:
            wavy_message(f"Failed with status code: {response.status_code}", Color.red, Color.red)
        logs = read_json(FILES["webhook_delete_history"])
        logs.append({"webhook": webhook, "status": response.status_code, "timestamp": str(datetime.utcnow())})
        write_json(FILES["webhook_delete_history"], logs)
    except Exception as e:
        wavy_message(f"Error: {e}", Color.red, Color.red)
    input("\nPress Enter to continue...")

def webhook_info():
    webhook = input("\nEnter webhook URL to get info: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    wavy_message("Fetching webhook info...", Color.cyan, Color.blue)
    try:
        response = requests.get(webhook)
        if response.status_code == 200:
            data = response.json()
            wavy_message("Webhook Information:", Color.cyan, Color.blue)
            wavy_message(f"Name       : {data.get('name')}", Color.green, Color.light_green)
            wavy_message(f"ID         : {data.get('id')}", Color.green, Color.light_green)
            wavy_message(f"Channel ID : {data.get('channel_id')}", Color.green, Color.light_green)
            wavy_message(f"Guild ID   : {data.get('guild_id')}", Color.green, Color.light_green)
            created_timestamp = ((int(data.get('id')) >> 22) + 1420070400000) / 1000
            created_date = datetime.utcfromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
            wavy_message(f"Created At : {created_date}", Color.green, Color.light_green)
        else:
            wavy_message(f"Failed to get info. Status code: {response.status_code}", Color.red, Color.red)
    except Exception as e:
        wavy_message(f"Error: {e}", Color.red, Color.red)
    input("\nPress Enter to continue...")

def rename_webhook():
    webhook = input("\nEnter webhook URL: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    new_name = input("Enter new webhook name: ")
    wavy_message("Renaming webhook...", Color.cyan, Color.blue)
    try:
        response = requests.patch(webhook, json={"name": new_name})
        if response.status_code == 200:
            wavy_message(f"Webhook renamed to {new_name}", Color.green, Color.light_green)
        else:
            wavy_message(f"Failed to rename webhook. Status code: {response.status_code}", Color.red, Color.red)
        logs = read_json(FILES["webhook_rename_history"])
        logs.append({"webhook": webhook, "new_name": new_name, "status": response.status_code, "timestamp": str(datetime.utcnow())})
        write_json(FILES["webhook_rename_history"], logs)
    except Exception as e:
        wavy_message(f"Error: {e}", Color.red, Color.red)
    input("\nPress Enter to continue...")

def edit_webhook_image():
    webhook = input("\nEnter webhook URL: ")
    if not validate_webhook(webhook):
        wavy_message("[ERROR] Invalid webhook URL.", Color.red, Color.red)
        return
    new_avatar = input("Enter new avatar image URL (must end with .png or .jpg): ")
    if not (new_avatar.lower().endswith(".png") or new_avatar.lower().endswith(".jpg")):
        wavy_message("[ERROR] Avatar URL must be a .png or .jpg file.", Color.red, Color.red)
        return
    wavy_message("Updating webhook image...", Color.cyan, Color.blue)
    try:
        response = requests.patch(webhook, json={"avatar": new_avatar})
        if response.status_code == 200:
            wavy_message("Webhook image updated.", Color.green, Color.light_green)
        else:
            wavy_message(f"Failed to update image. Status code: {response.status_code}", Color.red, Color.red)
        logs = read_json(FILES["webhook_edit_image_history"])
        logs.append({"webhook": webhook, "avatar": new_avatar, "status": response.status_code, "timestamp": str(datetime.utcnow())})
        write_json(FILES["webhook_edit_image_history"], logs)
    except Exception as e:
        wavy_message(f"Error: {e}", Color.red, Color.red)
    input("\nPress Enter to continue...")

# ----------------------
# Token Functions
# ----------------------
def check_token(token):
    headers = {"Authorization": token}
    try:
        r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
        return r.status_code == 200
    except:
        return False

def generate_token():
    chars = string.ascii_letters + string.digits + '-_'
    return f"{''.join(random.choices(chars, k=24))}.{''.join(random.choices(chars, k=6))}.{''.join(random.choices(chars, k=27))}"

def token_generator():
    try:
        count = int(input("\nHow many tokens to generate?: "))
    except ValueError:
        wavy_message("Invalid input.", Color.red, Color.red)
        return

    wavy_message(f"Generating {count} tokens...", Color.cyan, Color.blue)

    def generate_and_check():
        token = generate_token()
        valid = check_token(token)
        return token, valid

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(generate_and_check) for _ in range(count)]
        for future in as_completed(futures):
            token, valid = future.result()
            if valid:
                gradient_print(f"Token {token} VALID", start_color=Color.green, end_color=Color.light_green)
                tokens = read_json(FILES["valid_tokens"])
                tokens.append(token)
                write_json(FILES["valid_tokens"], tokens)
            else:
                gradient_print(f"Token {token} INVALID", start_color=Color.red, end_color=Color.red)
                tokens = read_json(FILES["invalid_tokens"])
                tokens.append(token)
                write_json(FILES["invalid_tokens"], tokens)

    gradient_print("Token generation complete.", start_color=Color.cyan, end_color=Color.blue)
    input("\nPress Enter to continue...")

# ----------------------
# Main Program
# ----------------------
def main():
    init()
    while True:
        banner()
        choice = input("Select option: ")
        if choice == "1":
            send_webhook_message()
        elif choice == "2":
            spam_webhook()
        elif choice == "3":
            delete_webhook()
        elif choice == "4":
            webhook_info()
        elif choice == "5":
            token_generator()
        elif choice == "6":
            rename_webhook()
        elif choice == "7":
            edit_webhook_image()
        elif choice == "0":
            break
        else:
            wavy_message("Invalid Option.", Color.red, Color.blue)

if __name__ == "__main__":
    main()


