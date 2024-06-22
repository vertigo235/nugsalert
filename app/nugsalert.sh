#!/bin/bash

# Set UMASK to 002 to ensure files are editable by any user in the group
umask 002

# Define default user and group IDs
APP_USER_ID=${PUID:-}
APP_GROUP_ID=${PGID:-}

# Only create user and group if PUID and PGID are set
if [ -n "$APP_USER_ID" ] && [ -n "$APP_GROUP_ID" ]; then
    # Check if the group or GID already exists
    if ! getent group appgroup > /dev/null && ! getent group $APP_GROUP_ID > /dev/null; then
        groupadd -g $APP_GROUP_ID appgroup
    fi

    # Check if the user or UID already exists
    if ! getent passwd appuser > /dev/null && ! getent passwd $APP_USER_ID > /dev/null; then
        useradd -u $APP_USER_ID -g $APP_GROUP_ID -m appuser
    fi

    # Log the UID and GID that should be set
    echo "Setting UID to: $APP_USER_ID, GID to: $APP_GROUP_ID"
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

# Execute Python script conditionally
if [ -n "$APP_USER_ID" ] && [ -n "$APP_GROUP_ID" ]; then
    su appuser -c "echo 'Executing as UID:' \$(id -u) ', GID:' \$(id -g); python /app/nugsalert.py"
else
    echo 'Executing as current user'
    python /app/nugsalert.py
fi
