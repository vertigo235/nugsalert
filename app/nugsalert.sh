#!/bin/bash

# Define default user and group IDs
APP_USER_ID=${PUID:-1000}
APP_GROUP_ID=${PGID:-1000}

# Create a non-root user and group with customizable IDs
# Check if the group already exists
if ! getent group appgroup > /dev/null; then
    groupadd -g $APP_GROUP_ID appgroup
fi

# Check if the user already exists
if ! getent passwd appuser > /dev/null; then
    useradd -u $APP_USER_ID -g $APP_GROUP_ID -m appuser
fi
# Set default values for variables
EMAIL=${NUGS_EMAIL:-""}
PASSWORD=${NUGS_PASSWORD:-""}
FORMAT=${NUGS_FORMAT:-4}
VIDEO_FORMAT=${NUGS_VIDEO_FORMAT:-5}
OUT_PATH=${NUGS_OUT_PATH:-"/downloads"}
TOKEN=${NUGS_TOKEN:-}
USE_FFMPEG_ENV_VAR=${NUGS_USE_FFMPEG_ENV_VAR:-true}
JSON_FILE="/app/config.json"

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
  echo "nugs.net config file created: $JSON_FILE"
else
  echo "nugs.net config file already exists: $JSON_FILE"
fi

su appuser -c "python /app/nugsalert.py"