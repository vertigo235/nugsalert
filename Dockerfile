# Build Nugs-Dl
FROM golang:1.21.3-bullseye as build

WORKDIR /build

# Install dependencies and build the application
RUN apt update && apt install -y --no-install-recommends git ffmpeg && \
    git clone https://github.com/Sorrow446/Nugs-Downloader.git . && \
    go build -o Nugs-DL main.go structs.go

# Final Stage
FROM python:3.12-slim-bullseye
WORKDIR /app
COPY --from=build /build/Nugs-DL /app/Nugs-DL

# Copy the contents of the /app folder into the container
COPY ./app /app
RUN chmod +x /app/nugsalert.sh

# Install dependencies (assuming you have a requirements.txt)
RUN pip install -r /app/requirements.txt

# Set the FILE_PATH environment variable
ENV FILE_PATH=/data/

# Create a directory for downloads and set permissions
RUN mkdir /downloads && chmod 777 /downloads
RUN mkdir /data && chmod 777 /data

CMD ["/app/nugsalert.sh"]
