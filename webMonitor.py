from dotenv import load_dotenv
import os
import requests
import time
import logging
import sys
import threading

load_dotenv()


TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

WEBSITES = [
    "https://shegruh.com/",
    "https://shegruh.com/api/healthcheck",
    
]

CHECK_INTERVAL = 600  
TIMEOUT        = 10
BAD_STATUS_CODES = [400, 401, 403, 404, 500, 502, 503, 504]
# ──────────────────────────────────────────────────────

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

site_status = {}   
site_last_code = {}  

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            logging.error(f"Telegram error: {r.text}")
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        r = requests.get(url, params=params, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        logging.error(f"getUpdates failed: {e}")
        return []

def check_site(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code
    except requests.ConnectionError:
        return "CONNECTION_ERROR"
    except requests.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def status_emoji(code):
    if code == 403:
        return "🚫"
    if code == 404:
        return "🔍"
    if isinstance(code, int) and str(code).startswith("5"):
        return "💥"
    return "⚠️"

def handle_status_command():
    if not site_status:
        send_telegram("⏳ No sites checked yet. Please wait for first check cycle.")
        return
    lines = ["📊 <b>Current Site Status</b>\n"]
    for url in WEBSITES:
        st = site_status.get(url, "unknown")
        code = site_last_code.get(url, "N/A")
        if st == "up":
            lines.append(f"✅ <b>UP</b> ({code})\n{url}")
        elif st == "down":
            emoji = status_emoji(code) if isinstance(code, int) else "❌"
            lines.append(f"{emoji} <b>DOWN</b> ({code})\n{url}")
        else:
            lines.append(f"❓ <b>UNKNOWN</b>\n{url}")
    send_telegram("\n\n".join(lines))

def telegram_listener():
    offset = None
    logging.info("Telegram command listener started.")
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "").strip().lower()
            chat_id = str(message.get("chat", {}).get("id", ""))

           
            if chat_id != TELEGRAM_CHAT_ID:
                continue

            if text == "/status":
                handle_status_command()
            elif text == "/help":
                send_telegram(
                    "🤖 <b>Website Monitor Commands</b>\n\n"
                    "/status — Check all sites right now\n"
                    "/help — Show this help message\n\n"
                    "You will only get automatic alerts when a site goes <b>DOWN</b> or <b>RECOVERS</b>."
                )

def monitor_loop():
    for url in WEBSITES:
        site_status[url] = "up"
        site_last_code[url] = "N/A"

    logging.info("Website monitor started.")
    send_telegram(
        "✅ <b>Website Monitor is now running!</b>\n"
        "You'll only be notified when a site goes down or recovers.\n"
        "Type /status anytime to check all sites."
    )

    while True:
        for url in WEBSITES:
            code = check_site(url)
            site_last_code[url] = code
            is_bad = code in BAD_STATUS_CODES or isinstance(code, str)
            was_down = site_status.get(url) == "down"

            if is_bad and not was_down:
                site_status[url] = "down"
                emoji = status_emoji(code) if isinstance(code, int) else "❌"
                send_telegram(
                    f"{emoji} <b>SITE ALERT!</b>\n"
                    f"<b>URL:</b> {url}\n"
                    f"<b>Status:</b> {code}\n"
                    f"Type /status to see all sites."
                )
                logging.warning(f"ALERT: {url} returned {code}")

            elif not is_bad and was_down:
                site_status[url] = "up"
                send_telegram(
                    f"✅ <b>SITE RECOVERED!</b>\n"
                    f"<b>URL:</b> {url}\n"
                    f"<b>Status:</b> {code} — back to normal!"
                )
                logging.info(f"RECOVERED: {url} is back up with {code}")

            else:
                logging.info(f"OK: {url} → {code}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":

    listener_thread = threading.Thread(target=telegram_listener, daemon=True)
    listener_thread.start()


    monitor_loop()