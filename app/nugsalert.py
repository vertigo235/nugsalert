import requests
import os
import json
import logging
from decouple import config
import apprise

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurable values
URL_TEMPLATE = "https://catalog.nugs.net/api/v1/releases/recent?limit=20&offset=0&artistIds={}&contentType=audio"
ARTIST_ID = config('ARTIST_ID', default='')
URL = URL_TEMPLATE.format(ARTIST_ID)
FILE_PATH = "known_ids.json"
PUSHOVER_TOKEN = config('PUSHOVER_APP_TOKEN', default='')
PUSHOVER_USER = config('PUSHOVER_USER_KEY', default='')

def fetch_latest_data():
    logging.info("Fetching latest data from URL...")
    response = requests.get(URL)
    return response.json()['items']

def get_stored_ids():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        logging.warning(f"File {FILE_PATH} not found. Creating a new one...")
        with open(FILE_PATH, 'w') as file:
            json.dump([], file)
        return []

def store_ids(latest_ids):
    with open(FILE_PATH, 'w') as file:
        json.dump(latest_ids, file)

def send_pushover_notification(message, title):
    # Create an Apprise instance
    apobj = apprise.Apprise()

    # Define your Pushover server using the correct URL format:
    # pover://<user_token>@<app_token>
    url = f"pover://{PUSHOVER_USER}@{PUSHOVER_TOKEN}"

    # Add your notification service to apprise
    apobj.add(url)

    # Send your notification
    apobj.notify(body=message, title=title)

def main():
    logging.info("Application started.")
    latest_data = fetch_latest_data()
    latest_ids = [item['id'] for item in latest_data]
    stored_ids = get_stored_ids()

    new_records = [item for item in latest_data if item['id'] not in stored_ids]

    if new_records:
        logging.info(f"Found {len(new_records)} new records. Sending notification...")
        alert_msg_title = f"New content available on nugs.net!"
        digest_message = "\n".join([record['artist']['name'] + ' - ' + record['title'] for record in new_records])
        send_pushover_notification(digest_message, alert_msg_title)
        store_ids(latest_ids)
    else:
        logging.info("No new records found.")

if __name__ == "__main__":
    main()
