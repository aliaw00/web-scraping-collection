import subprocess
import logging

def send_alert(name, price):
    message = f"{name} dropped to €{price}"
    logging.info(f"ALERT: {message}")

    try:
        subprocess.run(["notify-send", "💰 Price Drop Guardian", message])
    except Exception as e:
        logging.error(f"Notification failed: {e}")
