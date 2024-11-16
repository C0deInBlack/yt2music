# yt-dlp-at
Download music from YouTube, add metadata and cover image.

**Updated with Cython !**

## Installation

```bash
sudo docker pull c0deinblack/yt-dlp-at:v1.5
```

For `zsh`, run the next commands to add the functions in your `.zshrc`

```bash
echo 'function yt_at_file(){ if [ "$#" -ne 3 ]; then echo -e "usage: $funcstack <path> <metadata> <file>"; else docker run -it --rm -v "$1":/app/data -v "$3":/app/"$(basename "$3")" c0deinblack/yt-dlp-at:v1.5 -m "$2" -f "$(basename "$3")"; fi }' >> ~/.zshrc

echo 'function yt_at_url(){ if [ "$#" -ne 3 ];then echo -e "usage: $funcstack <path> <metadata> <url>"; else docker run -it --rm -v "$1":/app/data c0deinblack/yt-dlp-at:v1.5 -m "$2" -u "$3";fi }' >> ~/.zshrc
```

For `bash`, run the next commands to add the functions in your `.bashrc`

```bash
echo 'function yt_at_file(){ if [ "$#" -ne 3 ]; then echo -e "usage: $FUNCNAME <path> <metadata> <file>"; else docker run -it --rm -v "$1":/app/data -v "$3":/app/"$(basename "$3")" c0deinblack/yt-dlp-at:v1.5 -m "$2" -f "$(basename "$3")"; fi }' >> ~/.bashrc

echo 'function yt_at_url(){ if [ "$#" -ne 3 ];then echo -e "usage: $FUNCNAME <path> <metadata> <url>"; else docker run -it --rm -v "$1":/app/data c0deinblack/yt-dlp-at:v1.5 -m "$2" -u "$3";fi }' >> ~/.bashrc
```

## Usage

```bash
usage: yt_at_url <path> <metadata> <url>
usage: yt_at_file <path> <metadata> <file>
```
### From URL

If you want to download from a url, just call the function with the arguments:

```bash
yt_at_url /path/to/your/music/artist Artist "https://www.youtube.com/@artist/releases"
```
**NOTE:** Don't write the metadata argument all in upper case, otherwise the program will fail. Why? I don't know. Things with python argparse.

I recommend use this option only if the link you are downloading have 'releases' in the url `https://www.youtube.com/@artist/releases` otherwise it will mess up and download all the songs in one directory instead of separated albums.

### From file

The best option is to download from a list, you have to save the links of the albums in a plain text file and call the function with its arguments:

```bash
yt_at_file /path/to/your/music/artist Artist /path/to/your/file/file.txt
```
The file to read only have to be one link per line:

```
https://www.youtube.com/playlist?list=OLAK5uy_mI7UDM5J5hMzEuJU3YtHAwNRYuXZ1C5eE
https://www.youtube.com/playlist?list=OLAK5uy_lG_TgjUku8iY7Fez8h8-OVbtjfajrXFjQ
https://www.youtube.com/playlist?list=OLAK5uy_mb6E4B-zH404-oNnTX7M7G3REvN-ZM1rE
https://www.youtube.com/playlist?list=OLAK5uy_k8K0UZjoN_EizF0w9WgNDSgjC6TokIWtU
```

In both options (with url or file) if the name of one of your directories or artist has spaces, you should write `directory\ name` or `artist\ name` or you can write it beetwenn `""`:

```bash
yt_at_file /path/to/your/music/artist\ name artist\ name /path/to/your/file/file.txt
yt_at_url "/path/to/your/music/artist" "Artist name" "https://www.youtube.com/@artist/releases"
```
