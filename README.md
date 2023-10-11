# Nugs Alert and Downloader [![Build Status](https://drone.gitea.blubeacon.com/api/badges/vertigo235/nugsalert/status.svg)](https://drone.gitea.blubeacon.com/vertigo235/nugsalert)

This Docker container checks for new content on nugs.net and downloads it if any new content is found.

## Environment Variables

- **ARTIST_ID**: The ID of the artist you want to check for new content. (e.g. '196') can also be a string of artists (e.g. '196,128')
- **FILE_PATH**: Path where the known IDs file will be stored. (Default is '/data/')
- **PUSHOVER_APP_TOKEN**: Your Pushover application token for notifications.
- **PUSHOVER_USER_KEY**: Your Pushover user key for notifications.
- **CHECKTIME**: Number of minutes the application should wait before checking for updates again. If not set, the application will only run once.
- **DOWNLOAD_SHOW**: If set to 'true', the script will attempt to download new shows using the /app/Nugs-DL tool.
- **NUGS_EMAIL**: Your nugs.net email.
- **NUGS_PASSWORD**: Your nugs.net password.
- **NUGS_FORMAT**: The audio format you prefer to download (default is 4).
- **NUGS_VIDEO_FORMAT**: The video format you prefer to download (default is 5).
- **NUGS_OUT_PATH**: Path where the downloaded content will be stored (default is '/downloads').
- **NUGS_TOKEN**: Nugs token if available.
- **NUGS_USE_FFMPEG_ENV_VAR**: Whether to use ffmpeg environment variable (default is 'true').

## Build and Run

To build the Docker image, navigate to the directory containing the Dockerfile and execute:

```
docker build -t nugsalert .
```

To run the Docker container:

```
docker run --rm -it \
  -v /path/on/host/downloads:/downloads:rw \
  -v /path/on/host/data:/data:rw \
  -e ARTIST_ID='196' \
  -e PUSHOVER_APP_TOKEN='your_token' \
  -e PUSHOVER_USER_KEY='your_key' \
  -e NUGS_USERNAME='your nugs.net username' \
  -e NUGS_PASSWORD='your nugs.net password' \
  -e DOWNLOAD_SHOW='true' \
  nugsalert
```

Replace `/path/on/host/` with your desired directory on the host system.

## Notes

Ensure you set the correct environment variables as per your requirements.

