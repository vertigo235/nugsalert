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
ARTIST_ID = config('ARTIST_ID', default='')
LIMIT = config('LIMIT', default=50, cast=int)
AUDIO_URL_TEMPLATE = f"https://catalog.nugs.net/api/v1/releases/recent?limit={LIMIT}&offset=0&artistIds={ARTIST_ID}&contentType=audio"
VIDEO_URL_TEMPLATE = f"https://catalog.nugs.net/api/v1/releases/recent?limit={LIMIT}&offset=0&artistIds={ARTIST_ID}&contentType=video"
AUDIO_URL = AUDIO_URL_TEMPLATE
VIDEO_URL = VIDEO_URL_TEMPLATE
logging.info('AUDIO_URL: ' + AUDIO_URL)
logging.info('VIDEO_URL: ' + VIDEO_URL)
FILE_PATH = config("FILE_PATH", "").rstrip('/')
if FILE_PATH:
    FILE_PATH += '/'
AUDIO_FILENAME = f"{FILE_PATH}known_ids.json"
VIDEO_FILENAME = f"{FILE_PATH}known_video_ids.json"
PUSHOVER_TOKEN = config('PUSHOVER_APP_TOKEN', default=None)
PUSHOVER_USER = config('PUSHOVER_USER_KEY', default=None)
DOWNLOAD_AUDIO = config('DOWNLOAD_AUDIO', default='false').lower() == 'true'
DOWNLOAD_VIDEO = config('DOWNLOAD_VIDEO', default='false').lower() == 'true'
AUDIO_DOWNLOAD_PATH = config('AUDIO_DOWNLOAD_PATH', default='/downloads/audio/')
VIDEO_DOWNLOAD_PATH = config('VIDEO_DOWNLOAD_PATH', default='/downloads/video/')

def fetch_latest_data(url):
    logging.info(f"Fetching latest data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad responses
        return response.json()['items']
    except requests.RequestException as error:
        logging.error(f"Failed to fetch data due to: {error}")
        return []

def get_stored_ids(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        logging.warning(f"File {filename} not found. Creating a new one...")
        with open(filename, 'w') as file:
            json.dump([], file)
        return []

def store_ids(latest_ids, filename):
    stored_ids = get_stored_ids(filename)
    all_ids = list(set(stored_ids + latest_ids))  # Merge and remove duplicates
    with open(filename, 'w') as file:
        json.dump(all_ids, file)

def send_pushover_notification(message, title):
    # Create an Apprise instance
    apobj = apprise.Apprise()

    # Define your Pushover server using the correct URL format:
    url = f"pover://{PUSHOVER_USER}@{PUSHOVER_TOKEN}"

    # Add your notification service to apprise
    apobj.add(url)

    # Send your notification
    apobj.notify(body=message, title=title)

def download_show(artist_name, show_id, force_video=False):
    """Downloads a show using the /app/Nugs-DL tool and returns its exit code."""
    formatted_artist_name = artist_name.replace('.', '_') # Remove . from folder name to prevent issue with CIFS share and folders ending with "." (eg. moe.)
    download_path = VIDEO_DOWNLOAD_PATH if force_video else AUDIO_DOWNLOAD_PATH
    cmd = ["/app/Nugs-DL", "-o", f"{download_path}/{formatted_artist_name}/"]
    if force_video:
        cmd.append("--force-video")
    cmd.append(f"https://play.nugs.net/release/{show_id}")
    logging.info(f"Nugs-DL command: {cmd}")
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
    # Process audio content
    latest_audio_data = fetch_latest_data(AUDIO_URL)
    latest_audio_ids = [item['id'] for item in latest_audio_data]
    stored_audio_ids = get_stored_ids(AUDIO_FILENAME)

    new_audio_records = [item for item in latest_audio_data if item['id'] not in stored_audio_ids]

    # Process video content
    latest_video_data = fetch_latest_data(VIDEO_URL)
    latest_video_ids = [item['id'] for item in latest_video_data]
    stored_video_ids = get_stored_ids(VIDEO_FILENAME)

    new_video_records = [item for item in latest_video_data if item['id'] not in stored_video_ids]

    # Process new audio records
    if new_audio_records:
        if DOWNLOAD_AUDIO:
            for record in new_audio_records:
                artist_name = record['artist']['name']
                show_id = record['id']
                exit_code = download_show(artist_name, show_id)

                # Check exit code and perform necessary actions
                if exit_code == 0:
                    logging.info(f"Successfully downloaded audio show with ID {show_id}.")
                else:
                    logging.warning(f"Failed to download audio show with ID {show_id}. Exit code: {exit_code}.")
                    # Sending a notification about the failure
                    failure_title = "Audio Show Download Failure!"
                    failure_message = f"Failed to download audio show '{record['title']}' with ID {show_id}. Exit code: {exit_code}."
                    send_pushover_notification(failure_message, failure_title)

        audio_digest_message = "\n".join([record['artist']['name'] + ' - ' + record['title'] for record in new_audio_records])
        audio_alert_msg_title = f"New audio content available on nugs.net!"
        if PUSHOVER_TOKEN:
            logging.info(f"Found {len(new_audio_records)} new audio records. Sending notification...")
            send_pushover_notification(audio_digest_message, audio_alert_msg_title)
        else:
            logging.info(f"Found {len(new_audio_records)} new audio records. Pushover credentials not defined so no notification was sent...")

        store_ids(latest_audio_ids, AUDIO_FILENAME)
    else:
        logging.info("No new audio records found.")

    # Process new video records
    if new_video_records:
        if DOWNLOAD_VIDEO:
            for record in new_video_records:
                artist_name = record['artist']['name']
                show_id = record['id']
                exit_code = download_show(artist_name, show_id, force_video=True)

                # Check exit code and perform necessary actions
                if exit_code == 0:
                    logging.info(f"Successfully downloaded video show with ID {show_id}.")
                else:
                    logging.warning(f"Failed to download video show with ID {show_id}. Exit code: {exit_code}.")
                    # Sending a notification about the failure
                    failure_title = "Video Show Download Failure!"
                    failure_message = f"Failed to download video show '{record['title']}' with ID {show_id}. Exit code: {exit_code}."
                    send_pushover_notification(failure_message, failure_title)

        video_digest_message = "\n".join([record['artist']['name'] + ' - ' + record['title'] for record in new_video_records])
        video_alert_msg_title = f"New video content available on nugs.net!"
        if PUSHOVER_TOKEN:
            logging.info(f"Found {len(new_video_records)} new video records. Sending notification...")
            send_pushover_notification(video_digest_message, video_alert_msg_title)
        else:
            logging.info(f"Found {len(new_video_records)} new video records. Pushover credentials not defined so no notification was sent...")

        store_ids(latest_video_ids, VIDEO_FILENAME)
    else:
        logging.info("No new video records found.")

if __name__ == "__main__":
    main()
