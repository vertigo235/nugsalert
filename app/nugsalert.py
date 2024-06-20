import requests
import os
import json
import logging
from decouple import config
import apprise
import time
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurable values
URL_TEMPLATE = f"https://catalog.nugs.net/api/v1/releases/recent?limit={LIMIT}&offset=0&artistIds={ARTIST_ID}&contentType=audio"
ARTIST_ID = config('ARTIST_ID', default='')
LIMIT = config('LIMIT', default=20, cast=int)
URL = URL_TEMPLATE.format(ARTIST_ID)
FILE_PATH = config("FILE_PATH", "").rstrip('/')
if FILE_PATH:
    FILE_PATH += '/'
FILENAME = f"{FILE_PATH}known_ids.json"
PUSHOVER_TOKEN = config('PUSHOVER_APP_TOKEN', default=None)
PUSHOVER_USER = config('PUSHOVER_USER_KEY', default=None)
DOWNLOAD_SHOW = config('DOWNLOAD_SHOW', default='false').lower() == 'true'


def fetch_latest_data():
    logging.info("Fetching latest data from URL...")
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise exception for bad responses
        return response.json()['items']
    except requests.RequestException as error:
        logging.error(f"Failed to fetch data due to: {error}")
        return []

def get_stored_ids():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    else:
        logging.warning(f"File {FILENAME} not found. Creating a new one...")
        with open(FILENAME, 'w') as file:
            json.dump([], file)
        return []

def store_ids(latest_ids):
    with open(FILENAME, 'w') as file:
        json.dump(latest_ids, file)

def send_pushover_notification(message, title):
    # Create an Apprise instance
    apobj = apprise.Apprise()

    # Define your Pushover server using the correct URL format:
    url = f"pover://{PUSHOVER_USER}@{PUSHOVER_TOKEN}"

    # Add your notification service to apprise
    apobj.add(url)

    # Send your notification
    apobj.notify(body=message, title=title)

def download_show(artist_name, show_id):
    """Downloads a show using the /app/Nugs-DL tool and returns its exit code."""
    formatted_artist_name = artist_name.replace('.', '_') # Remove . from folder name to prevent isse with CIFS share and folders ending with "." (eg. moe.)
    cmd = ["/app/Nugs-DL", "-o", f"/downloads/{formatted_artist_name}/", f"https://play.nugs.net/release/{show_id}"]
    result = subprocess.run(cmd)
    return result.returncode

def main():
    logging.info("Application started.")
    check_time = config('CHECKTIME', default=None)

    # If CHECKTIME is not defined or not a number, run the script once
    if not check_time or not check_time.isdigit():
        check_for_updates()
        return

    # If CHECKTIME is defined and a number, run the script every {n} minutes
    delay = int(check_time) * 60  # Convert minutes to seconds

    while True:
        check_for_updates()
        logging.info(f"Sleeping for {check_time} minutes...")
        time.sleep(delay)

def check_for_updates():
    latest_data = fetch_latest_data()
    latest_ids = [item['id'] for item in latest_data]
    stored_ids = get_stored_ids()

    new_records = [item for item in latest_data if item['id'] not in stored_ids]

    if new_records:
        if DOWNLOAD_SHOW:
            for record in new_records:
                artist_name = record['artist']['name']
                show_id = record['id']
                exit_code = download_show(artist_name, show_id)
                
                # Check exit code and perform necessary actions
                if exit_code == 0:
                    logging.info(f"Successfully downloaded show with ID {show_id}.")
                else:
                    logging.warning(f"Failed to download show with ID {show_id}. Exit code: {exit_code}.")
                    # Sending a notification about the failure
                    failure_title = "Show Download Failure!"
                    failure_message = f"Failed to download show '{record['title']}' with ID {show_id}. Exit code: {exit_code}."
                    send_pushover_notification(failure_message, failure_title)

        digest_message = "\n".join([record['artist']['name'] + ' - ' + record['title'] for record in new_records])
        alert_msg_title = f"New content available on nugs.net!"
        if PUSHOVER_TOKEN:
            logging.info(f"Found {len(new_records)} new records. Sending notification...")
            send_pushover_notification(digest_message, alert_msg_title)
        else:
            logging.info(f"Found {len(new_records)} new records. Pushover credntials not defined so no notification was sent...")
        
        store_ids(latest_ids)
    else:
        logging.info("No new records found.")

if __name__ == "__main__":
    main()
