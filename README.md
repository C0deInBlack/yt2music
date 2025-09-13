# yt2music
Download entire artist's music from YouTube: playlists, full albums, or song sections, with automatic metadata and cover image tagging. 

## News
Pure Python implementation, no docker container needed anymore!

![img](https://github.com/C0deInBlack/yt2music/blob/main/images/1.cleaned.png)

## Installation

```bash
git clone https://github.com/C0deInBlack/yt2music.git
chmod +x yt2music.py
```
Install libraries

```bash
pip install -r requirements.txt
```
Also need to have ImageMagick installed.

## Usage

```
 ./yt2music.py
__   ___   ____                      _
\ \ / / |_|___ \ _ __ ___  _   _ ___(_) ___
 \ V /| __| __) | '_ ` _ \| | | / __| |/ __|
  | | | |_ / __/| | | | | | |_| \__ \ | (__
  |_|  \__|_____|_| |_| |_|\__,_|___/_|\___|


usage: yt2music.py [-h] [-p PATH] [-m METADATA] [-f FILE] [-u URL] [-s SECTIONS] [-sf SECTIONS_FILE] [-st SECTIONS_TITLE]

Script for download YT music

options:
  -h, --help            show this help message and exit
  -p, --path PATH       Path to save the music [Text Input]
  -m, --metadata METADATA
                        Metadata (Artist name) [Text Input]
  -f, --file FILE       Custom urls to read [File]
  -u, --url URL         Url to download music from [Text Input]
  -s, --sections SECTIONS
                        Download sections [True / False] (Default is False)
  -sf, --sections_file SECTIONS_FILE
                        Sections to download [File]
  -st, --sections_title SECTIONS_TITLE
                        Use the sections title [True / False] (Default is False)

Examples:
Download from a URL:
./yt2music.py -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'

Read from a file:
./yt2music.py -p /path/artist -m 'Artist name' -f /path/to/list.txt

Download sections and use custom names for the songs:
./yt2music.py -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -sn /path/names.txt -u 'http://www.youtube.com/example'

Download sections and use default titles from the videos:
./yt2music.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://www.youtube.com/example'
```

**NOTE:** Don't write the metadata argument all in upper case, otherwise the program will fail. Why? I don't know. Things with python argparse.

### Download from URL

```bash
./yt2music.py -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'
```

I recommend download from a url only if the link you are downloading have 'releases' in the url `https://www.youtube.com/@artist/releases` otherwise it will mess up and download all the songs in one directory instead of separated albums.

### Download from file

```bash
./yt2music.py -p /path/artist -m 'Artist name' -f /path/to/list.txt
```

The best option is to download from a list, you have to save the links of the albums playlists in a plain text file. The file to read only have to be one link per line:

```
https://www.youtube.com/playlist?list=OLAK5uy_mI7UDM5J5hMzEuJU3YtHAwNRYuXZ1C5eE
https://www.youtube.com/playlist?list=OLAK5uy_lG_TgjUku8iY7Fez8h8-OVbtjfajrXFjQ
https://www.youtube.com/playlist?list=OLAK5uy_mb6E4B-zH404-oNnTX7M7G3REvN-ZM1rE
https://www.youtube.com/playlist?list=OLAK5uy_k8K0UZjoN_EizF0w9WgNDSgjC6TokIWtU
```

In both options (with url or file) if the name of one of your directories or artist has spaces, you should write `directory\ name` or `artist\ name` or you can write it between `"Artist name"` or `'Artist name'`:

### Download sections

For download separated sections from a single video, you have two options:

#### First Option (Sections)

A sections file with the start time and the name of each song in the next format:

```bash
00:00 Song_title 1
00:20 Song_title 2
04:11 Song_title 3
10:16 Song_title 4
15:06 Song_title 5
18:47 Song_title 6
```

This will download the specified sections and add the custom title you provided.

```bash
./yt2music.py -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -u 'http://www.youtube.com/example'
```
#### Second Option (Sections)

Or use the default sections title for the video (which not always work), and add it to the sections file, usually the sections names are in the description of the YouTube video

```bash
Default_section_name 1
Default_section_name 2
Default_section_name 3
Default_section_name 4
Default_section_name 5
Default_section_name 6
```

This will download the sections and add the default name from the YouTube video

```bash
./yt2music.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://ww.youtube.com/example'
```

## Note

If you get an error downloading multiple songs, consider reinstalling yt-dlp (which is listed in requirements.txt) because the team of yt-dlp are constantly working to make the library work [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Extra
For a more specific example of use visit [example](https://medium.com/@c0deinblack/yt2music-download-entire-artist-discographies-from-youtube-6210ff169897)

