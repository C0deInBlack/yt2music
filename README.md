# yt-dlp-at
Download music from YouTube, add metadata and cover image.

**Made with Cython**

## Installation

```bash
sudo docker pull c0deinblack/yt-dlp-at:v1.6
```

Then clone the repository:

```bash
git clone https://github.com/C0deInBlack/yt-dlp-at.git
chmod +x yt_dlp_at.py
```

## Usage

```bash
./yt_dlp_at.py
usage: yt_dlp_at.py [-h] [-p PATH] [-m METADATA] [-f FILE] [-u URL] [-s SECTIONS]
                    [-sf SECTIONS_FILE] [-sn SECTIONS_NAMES] [-st SECTIONS_TITLE]

Script for download YT music

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to save the music [Text Input]
  -m METADATA, --metadata METADATA
                        Metadata (Artist name) [Text Input]
  -f FILE, --file FILE  Custom urls to read [File]
  -u URL, --url URL     Url to download music from [Text Input]
  -s SECTIONS, --sections SECTIONS
                        Download sections [True / False] (Default is False)
  -sf SECTIONS_FILE, --sections_file SECTIONS_FILE
                        Sections to download [File]
  -sn SECTIONS_NAMES, --sections_names SECTIONS_NAMES
                        Names of the sections [File]
  -st SECTIONS_TITLE, --sections_title SECTIONS_TITLE
                        Use the sections title [True / False] (Default is False)

Examples:
Download from a URL:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'

Read from a file:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -f /path/to/list.txt

Download sections and use custom names for the songs:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -sn /path/names.txt -u 'http://www.youtube.com/example'

Download sections and use default titles from the videos:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://ww.youtube.com/example'
```

**NOTE:** Don't write the metadata argument all in upper case, otherwise the program will fail. Why? I don't know. Things with python argparse.

### Download from URL

```bash
./yt_dlp_at.py -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'
```

I recommend download from a url only if the link you are downloading have 'releases' in the url `https://www.youtube.com/@artist/releases` otherwise it will mess up and download all the songs in one directory instead of separated albums.

### Download from file

```bash
./yt_dlp_at.py -p /path/artist -m 'Artist name' -f /path/to/list.txt
```

The best option is to download from a list, you have to save the links of the albums playlists in a plain text file. The file to read only have to be one link per line:

```
https://www.youtube.com/playlist?list=OLAK5uy_mI7UDM5J5hMzEuJU3YtHAwNRYuXZ1C5eE
https://www.youtube.com/playlist?list=OLAK5uy_lG_TgjUku8iY7Fez8h8-OVbtjfajrXFjQ
https://www.youtube.com/playlist?list=OLAK5uy_mb6E4B-zH404-oNnTX7M7G3REvN-ZM1rE
https://www.youtube.com/playlist?list=OLAK5uy_k8K0UZjoN_EizF0w9WgNDSgjC6TokIWtU
```

In both options (with url or file) if the name of one of your directories or artist has spaces, you should write `directory\ name` or `artist\ name` or you can write it beetwenn `"Artist name"` or `'Artist name'`:

### Download sections

For download separated sections from a single video, you have two options:

#### Fisrt Option (Sections)

A sections file with the duration of the each song in the next format

```bash
00:00-00:20
00:20-04:11
04:11-10:16
10:16-15:06
15:06:18:47
18:47-24:59
```

And a sections names file with the the title you want for each song.

```bash
Song_title 1
Song_title 2
Song_title 3
Song_title 4
Song_title 5
Song_title 6
```

This will download the specified sections and add the custom title you provide in the sections name file.

```bash
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -sn /path/names.txt -u 'http://www.youtube.com/example'
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
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://ww.youtube.com/example'
```

