#!/usr/bin/bash

if [ "$#" -ne 3 ] && [ "$#" -ne 4 ]; then
  echo -e "\n[!] Usage: $BASH_SOURCE <path> <filename> <metadata> <url>"
  exit 1
fi

path=$1
filename=$2
metadata=$3
url=$4

if [ "$(id -u)" -ne 0 ]; then
  echo -e "\n[!] Run as root.\n"
  exit 1
else
  if [ -n "$url" ]; then
    sudo docker run -it --rm --name yt-dlp -v "$path":/app/data c0deinblack/yt-dlp-at:v1.4 -m "$metadata" -u "$url"
  else
    sudo docker run -it --rm --name yt-dlp -v "$path":/app/data -v "$filename":/app/"$(basename "$filename")" c0deinblack/yt-dlp-at:v1.4 -m "$metadata" -f "$(basename "$filename")"
  fi
fi
