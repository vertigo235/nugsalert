# NugsAlert

NugsAlert is a Dockerized Python application that fetches the latest audio releases of specific artists from nugs.net and sends notifications for new records via Pushover. It's designed to help fans stay updated on the latest releases without manually checking the site.

## Features

- Fetches latest data from nugs.net for a specified artist.
- Notifies users via Pushover for new releases.
- Can be configured to run once or at specified intervals.
- Dockerized for easy deployment and scaling.

## Prerequisites

- Docker or Podman installed on your system.
- Pushover account with user and app tokens for notifications.

## Building the Docker Image

To construct the Docker image, execute:

```
docker build -t nugsalert:latest .
```

## Running the Docker Container

Launch the Docker container using the command below:

```
docker run --rm -it -v /path/on/host/config.json:/app/config.json -v /path/on/host:/downloads:rw -e PUID=<YourUserID> -e PGID=<YourGroupID> nugsalert:latest
```

Replace `/path/on/host` with the appropriate directory on your host system where you desire to store data.

## Configuration

Several environment variables enable customization of the application's behavior:

- `PUID`: Specify the user ID the application should run under in the container. Defaults to 1000.
- `PGID`: Define the group ID the application should run under inside the container. Defaults to 1000.
- `ARTIST_ID`: Artist ID from nugs.net for which you want to fetch the latest releases. If not specified, it defaults to `196` (e.g., a specific band).
- `FILE_PATH`: Path where the application will store a JSON file with known record IDs. This allows the application to determine new records on subsequent runs. Defaults to `/data/`.
- `PUSHOVER_APP_TOKEN`: Your Pushover application token, necessary to send notifications.
- `PUSHOVER_USER_KEY`: Your Pushover user key, which determines where the notifications will be sent.
- `CHECKTIME`: If specified, the script will run continuously, checking for new data every `CHECKTIME` minutes. If not set, the script will execute once and exit.

## Contributing

We appreciate and welcome any contributions. If you have suggestions, enhancements, or encounter issues, please open an issue or submit a pull request.

## License

This project is released under the open-source [MIT License](LICENSE).
