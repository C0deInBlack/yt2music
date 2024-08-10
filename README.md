# yt-dlp-at
Download music from YouTube, add metadata and cover image.

## Installation

```bash
sudo docker pull c0deinblack/yt-dlp-at:v1.3  
```

## Usage

To following is a script for use more easily the image, it takes four arguments the path where you want to save the music, the filename to read the links, the artist name to add as metadata and the url:

```bash
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
    sudo docker run -it --rm --name yt-dlp -v "$path":/app/data c0deinblack/yt-dlp-at:v1.3 -m "$metadata" -u "$url"
  else
    sudo docker run -it --rm --name yt-dlp -v "$path":/app/data -v "$filename":/app/"$(basename "$filename")" c0deinblack/yt-dlp-at:v1.3 -m "$metadata" -f "$(basename "$filename")"
  fi
fi
```

Save the script with the name `yt-dlp-run.sh`(or other name if you want) and add execution permission:

```bash
chmod +x yt-dlp-run.sh
```

```bash
sudo ./yt-dlp-run.sh
[!] Usage: ./yt-dlp-run.sh <path> <filename> <metadata> <url>
```

If you want to download from a url, use the next arguments in the script:

```bash
 sudo ./yt-dlp-run.sh /path/to/your/music/artist . Artist https://www.youtube.com/@artist/releases
```

I recommend use this option only if the link you are downloading have 'releases' in the url `https://www.youtube.com/@artist/releases`.

The best option is to download from a list, you have to save the links of the albums in a plain text file and use the next command:

```bash
 sudo ./yt-dlp-run.sh /path/to/your/music/artist /path/to/your/file/file.txt  Artist
```
The file to read only have to be one link per line:

```
https://www.youtube.com/playlist?list=OLAK5uy_mI7UDM5J5hMzEuJU3YtHAwNRYuXZ1C5eE
https://www.youtube.com/playlist?list=OLAK5uy_lG_TgjUku8iY7Fez8h8-OVbtjfajrXFjQ
https://www.youtube.com/playlist?list=OLAK5uy_mb6E4B-zH404-oNnTX7M7G3REvN-ZM1rE
https://www.youtube.com/playlist?list=OLAK5uy_k8K0UZjoN_EizF0w9WgNDSgjC6TokIWtU
```

In both options (with url or file) if the name of one of your directories or artist has spaces, you should write `directory\ name` or `artist\ name`:

```bash
 sudo ./yt-dlp-run.sh /path/to/your/music/artist\ name /path/to/your/file/file.txt  artist\ name
```
