#!/bin/bash

# Define default user and group IDs
APP_USER_ID=${PUID:-1000}
APP_GROUP_ID=${PGID:-1000}

# Create a non-root user and group with customizable IDs
groupadd -g $APP_GROUP_ID appgroup
useradd -u $APP_USER_ID -g $APP_GROUP_ID -m appuser

# Set default values for variables
EMAIL=${EMAIL:-"youremail@email.com"}
PASSWORD=${PASSWORD:-"your_password"}
FORMAT=${FORMAT:-4}
VIDEO_FORMAT=${VIDEO_FORMAT:-5}
OUT_PATH=${OUT_PATH:-"/downloads"}
TOKEN=${TOKEN:-}
USE_FFMPEG_ENV_VAR=${USE_FFMPEG_ENV_VAR:-true}
JSON_FILE="/config/config.json"

# Check if the config file already exists
if [ ! -f "$JSON_FILE" ]; then
  # Create the JSON configuration in the /app/ folder
  cat <<EOF > "$JSON_FILE"
{
    "email": "$EMAIL",
    "password": "$PASSWORD",
    "format": $FORMAT,
    "videoFormat": $VIDEO_FORMAT,
    "outPath": "$OUT_PATH",
    "token": "$TOKEN",
    "useFfmpegEnvVar": $USE_FFMPEG_ENV_VAR
}
EOF
  echo "Config file created: $JSON_FILE"
else
  echo "Config file already exists: $JSON_FILE"
fi

# Execute the application with optional arguments
su appuser -c "python" "/app/nugsalert.py"