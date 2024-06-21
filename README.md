# Nugs Alert and Downloader [![Build Status](https://drone.gitea.blubeacon.com/api/badges/vertigo235/nugsalert/status.svg)](https://drone.gitea.blubeacon.com/vertigo235/nugsalert)

This Docker container checks for new content on nugs.net and downloads it if any new content is found.

## Environment Variables

- **ARTIST_ID**: The ID of the artist you want to check for new content. (e.g. '196') can also be a string of artists (e.g. '196,128')
- **FILE_PATH**: Path where the known IDs file will be stored. (Default is '/data/')
- **PUSHOVER_APP_TOKEN**: Your Pushover application token for notifications.
- **PUSHOVER_USER_KEY**: Your Pushover user key for notifications.
- **CHECKTIME**: Number of minutes the application should wait before checking for updates again. If not set, the application will only run once.
- **DOWNLOAD_AUDIO**: If set to 'true', the script will attempt to download new shows using the /app/Nugs-DL tool.
- **DOWNLOAD_VIDEO**: If set to 'true', the script will attempt to download new shows using the /app/Nugs-DL tool.
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

## Docker Image
You can also pull the Docker image for this project directly from Docker Hub:
```
docker pull docker.io/vertigo235/nugsalert
```

## Docker Compose

For a more streamlined deployment, especially when running multiple containers, you can use Docker Compose. Below is a sample `docker-compose.yml` configuration for `nugsalert`:

```yaml
version: '3.8'

services:
  nugsalert:
    image: vertigo235/nugsalert:latest
    container_name: nugsalert
    restart: unless-stopped
    environment:
      NUGS_EMAIL: your_email@example.com
      NUGS_PASSWORD: 'your_password'
      CHECKTIME: "5"
      PUSHOVER_APP_TOKEN: your_pushover_app_token
      PUSHOVER_USER_KEY: your_pushover_user_key
      ARTIST_ID: "101,128,196"
      DOWNLOAD_SHOW: "true"
      PUID: "1000"
      PGID: "100"
      TZ: "US/Eastern"
    volumes:
      - /path_on_host/to/data:/data
      - /path_on_host/to/downloads:/downloads

```

To deploy using Docker Compose, navigate to the directory containing your `docker-compose.yml` and run:

```bash
docker-compose up -d
```

Remember to replace placeholder values like `your_email@example.com` with your actual data. If your password or any other values have special characters, ensure they're enclosed in single quotes for proper parsing.

## Credits
This docker uses the [Nugs-Downloader](https://github.com/Sorrow446/Nugs-Downloader) project by [Sorrow446](https://github.com/Sorrow446). A huge thanks to them for their contribution to the community!

