#!/usr/bin/python3

"""
Version: v2.4 
Author: https://github.com/C0deInBlack
"""

import argparse, json, os, sys, signal, shutil, textwrap, re, time, pdb
#sys.path.append('./LIBS/lib/python3.13/site-packages')
import requests
from termcolor import colored
import pyfiglet
from contextlib import redirect_stdout, redirect_stderr
import io

sys.path.append('LIBS/lib/python3.13/site-packages/')
from rich.console import Console
from rich.progress import Progress

from yt_dlp import YoutubeDL
import yt_dlp
from yt_dlp.utils import download_range_func
import eyed3
from wand.image import Image

# =============================================================================================
CURRENT_NAME: str # global variable to save the name of the current downloading album
console = Console() # Global console
# =============================================================================================

def sig_handler(sig, fram) -> None:
    global CURRENT_NAME
    global console
    try: shutil.rmtree(os.path.join(CURRENT_NAME))  # delete the current dowloading folder if CTRL-C
    except Exception as e: pass
    console.print("\n\n[red][!] Exiting\n"); sys.exit(0)

# ==================================================================================================================================
signal.signal(signal.SIGINT, sig_handler) # control-c handler function
# ==================================================================================================================================

def saveName(name: str) -> None: 
    """
    modify the name of the current downloading album through the global var
    """
    global CURRENT_NAME; CURRENT_NAME = name

# ==================================================================================================================================
def getNames(file_: str) -> tuple[list[str], list[str]]:
    """
    take the file with the urls and return two lists,
    one with the albums names and other with the total songs of each album
    """
    names: list = [] 
    total_songs: list = []
    # file_ var is where the playlist urls are
    with open(file_, 'r') as f: lines = f.readlines()
    for i in lines:
        opts = {
            'dump_single_json': True, 
            'extract_flat': 'in_playlist', 
            'noprogress': True,
            'quiet': True,
            'simulate': True,
            'noprogress' : True
        }

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            # Strip the string to avoid conflicts
            with YoutubeDL(opts) as ytdl: albums_names = ytdl.extract_info(i.strip(), download=False)
        
        json_string = json.dumps(albums_names) # Convert dict into json string
        x = json.loads(json_string) 
        
        names.append(x['title'])
        lenght = [i['title'] for i in x['entries']] # Get each song name
        total_songs.append(len(lenght)) # Total of songs
    return names, total_songs

# ==================================================================================================================================
def createUrls(url: str, file_name: str) -> str:
    """
    create the urls file 
    """
    opts = {
        'extract_flat': 'in_playlist',
        'fragment_retries': 10,
        'ignoreerrors': True,
        'postprocessors': [{'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}],
        'print_to_file': {'video': [('url', file_name)]},
        'retries': 10,
        'noprogress' : True
    }
    
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        with YoutubeDL(opts) as ytdl: ytdl.download(url)

    return file_name

# ==================================================================================================================================
def rmSpecialChracters(name: str) -> str: 
    """
    change conflicting characters from the album name
    """
    table = str.maketrans({
        '\\':'-',
        '/':'-',
        ':':'-',
        '*':'-',
        '?':'-',
        '"':'-',
        '<':'-',
        '>':'-',
        '|':'-',
    })
    return name.translate(table)

# ==================================================================================================================================
def downloadUrls(use_url: bool, file: str, url: str, metadata: str, app_path: str) -> None:
    """
    download the songs reading the urls from a file 
    and add metadata and cover image
    """
    global console
    start_time = time.time()
    file_name = file if not use_url else createUrls(url, 'url.txt') # create the urls file if not provided
    
    os.makedirs(app_path, exist_ok=True) # create the directory to save the music, pass if already exist
    names, total_songs = getNames(file_name)
    album_names = [rmSpecialChracters(i) for i in names]
  
    with open(file_name) as f: file = [i.strip() for i in f.readlines()]
   
    index_: int = 0 
    counter_: int = 0

    with Progress() as progress:
        task1 = progress.add_task("[*] Downloading", total=len(file))
        for index, link in enumerate(file):
            index_ = index

            album_path = os.path.join(app_path, album_names[index])
            saveName(album_path)

            progress.update(task1, advance=0, description="[*] Downloading %i of %i" % (index+1, len(file)))
            progress.refresh()

            try: os.makedirs(album_path)
            except FileExistsError:
                progress.update(task1, advance=1, description="[*] Downloading %i of %i" % (index+1, len(file)))
                progress.refresh()
                continue
           
            opts1 = {
                'extract_flat': 'discard_in_playlist',
                'final_ext': 'mp3',
                'format': 'bestaudio/best',
                'fragment_retries': 10,
                'ignoreerrors': 'only_download',
                'outtmpl': {'default': '%(playlist_index)s-%(title)s.%(ext)s'},
                'paths': {'home': os.path.join(album_path)},
                'postprocessors': [{'key': 'FFmpegExtractAudio',
                                    'nopostoverwrites': False,
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '0'},
                                   {'key': 'FFmpegConcat',
                                    'only_multi_video': True,
                                    'when': 'playlist'}],
                'retries': 10,
                'noprogress' : True
            }

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with YoutubeDL(opts1) as ytdl: ytdl.download(link)

            opts2 = {
                'extract_flat': 'in_playlist',
                'fragment_retries': 10,
                'ignoreerrors': 'only_download',
                'outtmpl': {'default': f'{album_names[index]}.%(ext)s'},
                'paths': {'home': os.path.join(album_path)},
                'postprocessors': [{'key': 'FFmpegConcat',
                                    'only_multi_video': True,
                                    'when': 'playlist'}],
                'retries': 10,
                'writethumbnail': True,
                'noprogress' : True
            }

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with YoutubeDL(opts2) as ytdl: ytdl.download(link)
 
            progress.update(task1, advance=1, description="[*] Downloading %i of %i" % (index+1, len(file)))
            progress.refresh()

            # add the metadata
            for counter, song in enumerate(sorted(os.listdir(album_path))):
                counter_ = counter
                if song.endswith('.mp3'):
                    image = os.path.join(album_path, f"{album_names[index]}.jpg")
                    # Load the song  
                    audiofile = eyed3.load(os.path.join(album_path, song))
                    # Initialize the tags
                    if not audiofile.tag: audiofile.initTag()
                    
                    audiofile.tag.artist = metadata
                    audiofile.tag.album = album_names[index]
                    audiofile.tag.track_num = counter+1
                    # Set the front cover
                    with open(image, 'rb') as cover_image: audiofile.tag.images.set(3, cover_image.read(), 'image/jpeg')
                    audiofile.tag.save()

            if total_songs[index_] != counter_: print(''); console.log("Failed downloading %d songs in %s" % (int(total_songs[index_])-int(counter_), album_names[index_]))
    end_time = time.time(); print(''); console.log("Finished in %i minutes" % ((end_time-start_time)/60))

# ==================================================================================================================================
def downloadSections(file: str, url: str, app_path: str, sections_title: bool, metadata: str) -> None:
    """
    download sections from a video and save it as individual songs,
    the file to read must have the sections to extract in the next format: "00:00-05:10,05:10-10:00"
    or the section title if is available
    """
    global console
    start_time = time.time()

    os.makedirs(app_path, exist_ok=True )# create the directory to save the music, pass if already exist
    with open(file) as f: lines = f.readlines() # Open the file and save it in a list

    if not sections_title: # if the names of the sections are provided with a file, read it 
        # Search for minutes expression 00:00
        sections_1 = [re.search(r'[\d]{2}:[\d]{2}', i).group() for i in lines]
        # Search for hours expression 00:00:00
        sections_2 = [re.search(r'[\d]{2}:[\d]{2}:[\d]{2}', i) for i in lines]
        # Replace hour expression in the original list
        sections_1 = [exp.group() if exp else org for org, exp in zip(sections_1, sections_2)]
        # Create a names list replacing the time expression 
        sections_names = [line.replace(reg, '').strip() for line, reg in zip(lines, sections_1)]
        sections_names = [rmSpecialChracters(i) for i in sections_names]
        
        # Replace the list with the proper start and end time expression 00:00-00:00
        sections_1 = [f"{sections_1[i]}-{sections_1[i+1]}" if i+1 < len(sections_1) else sections_1[i] for i in range(len(sections_1))]
        # Get the duration of the video
        opts1 = {
            'extract_flat': 'discard_in_playlist',
            'forceprint': {'video': ['--duration_string']},
            'fragment_retries': 10,
            'ignoreerrors': 'only_download',
            'noprogress': True,
            'postprocessors': [{'key': 'FFmpegConcat',
                                'only_multi_video': True,
                                'when': 'playlist'}],
            'quiet': True,
            'retries': 10,
            'simulate': True
        }

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with YoutubeDL(opts1) as ytdl: duration = ytdl.extract_info(url, download=False)

        # Add the duration of the video in the las section
        sections_1[-1] = f"{sections_1[-1]}-{duration['duration_string']}"
        
    # get the name of the video and save it as album name
    opts2 = {
        'dump_single_json': True,
        'extract_flat': 'in_playlist',
        'fragment_retries': 10,
        'ignoreerrors': 'only_download',
        'noprogress': True,
        'postprocessors': [{'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}],
        'quiet': True,
        'retries': 10,
        'simulate': True
    }

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        with YoutubeDL(opts2) as ytdl: album_name = ytdl.extract_info(url, download=False)

    json_string = json.dumps(album_name) # Convert dict into json string
    x = json.loads(json_string) 

    album = x['title']

    with Progress() as progress:
        task1 = progress.add_task("[*] Downloading", total=len(file))
        for index, section in enumerate(lines):
            progress.update(task1, advance=0, description="[*] Downloading Section %i of %i" % (index+1, len(lines)))
            progress.refresh()
            if sections_title:
                opts3 = {
                    'download_ranges': download_range_func([re.compile(f'{section}')], []),
                    'extract_flat': 'discard_in_playlist',
                    'final_ext': 'mp3',
                    'format': 'bestaudio/best',
                    'fragment_retries': 10,
                    'ignoreerrors': 'only_download',
                    'outtmpl': {'default': f'{index+1}-%(section_title)s-%(ext)s'},
                    'paths': {'home': os.path.join(app_path)},
                    'postprocessors': [{'key': 'FFmpegExtractAudio',
                                        'nopostoverwrites': False,
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '0'},
                                       {'key': 'FFmpegConcat',
                                        'only_multi_video': True,
                                        'when': 'playlist'}],
                    'retries': 10,
                    'noprogress' : True,
                    'postprocessors_args': {'ffmpeg':['-loglevel', 'panic', '-hide_banner', '-nostats', '-nostdin']}
                }
                  
                with open(os.devnull, 'w') as devnull:
                    with redirect_stdout(devnull), redirect_stderr(devnull):
                        with YoutubeDL(opts3) as ytdl: 
                            ytdl.download(url)

            else:
                # Format time 00:00-02:30 to seconds 0.0, 150.0
                if sections_1[index].count(':') == 2:
                    sections_formated = [float(i.split(':')[0])*60+float(i.split(':')[1]) for i in sections_1[index].split('-')]
                elif sections_1[index].count(':') == 4:
                    sections_formated = [float(i.split(':')[0])*3600+float(i.split(':')[1])*60+float(i.split(':')[2]) for i in sections_1[index].split('-')]
                opts4 = {
                    'download_ranges': download_range_func([], [sections_formated]),
                    'extract_flat': 'discard_in_playlist',
                    'final_ext': 'mp3',
                    'format': 'bestaudio/best',
                    'fragment_retries': 10,
                    'ignoreerrors': 'only_download',
                    'outtmpl': {'default': f'{index+1}-{sections_names[index]}.%(ext)s'},
                    'paths': {'home': os.path.join(app_path)},
                    'postprocessors': [{'key': 'FFmpegExtractAudio',
                                        'nopostoverwrites': False,
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '0'},
                                       {'key': 'FFmpegConcat',
                                        'only_multi_video': True,
                                        'when': 'playlist'}],
                    'retries': 10,
                    'noprogress' : True,
                    'postprocessors_args': {'ffmpeg':['-loglevel', 'panic', '-hide_banner', '-nostats', '-nostdin']}
                }
                
                with open(os.devnull, 'w') as devnull:
                    with redirect_stdout(devnull), redirect_stderr(devnull):
                        with YoutubeDL(opts4) as ytdl: 
                            ytdl.download(url)
 
            progress.update(task1, advance=1, description="[*] Downloading Section %i of %i" % (index+1, len(lines)))
            progress.refresh()

    # save the thumbnail
    opts5 = {
        'extract_flat': 'in_playlist',
        'fragment_retries': 10,
        'ignoreerrors': 'only_download',
        'outtmpl': {'default': f'{album}.%(ext)s'},
        'paths': {'home': os.path.join(app_path)},
        'postprocessors': [{'key': 'FFmpegConcat',
                            'only_multi_video': True,
                            'when': 'playlist'}],
        'retries': 10,
        'writethumbnail': True,
        'noprogress' : True
    }

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        with YoutubeDL(opts5) as ytdl: ytdl.download(url)

    # convert the webp to jpg for better image quality 
    img_webp = Image(filename=os.path.join(app_path, f"{album}.webp")) 
    img_jpg = img_webp.convert('jpg')
    img_jpg.save(filename=os.path.join(app_path, f"{album}.jpg"))

    # Clean the directory, remove the video file downloaded
    try: [os.remove(os.path.join(app_path, i)) for i in os.listdir(os.path.join(app_path)) if i.endswith('.webp') or i.endswith('.mkv') or i.endswith('.mp4') or i.endswith('.webm')]
    except: pass

    # add the metadata
    for counter, song in enumerate(sorted(os.listdir(app_path))):
        if song.endswith('.mp3'):
            image = os.path.join(app_path, f"{album}.jpg")
            # Load the song  
            audiofile = eyed3.load(os.path.join(app_path, song))
            # Initialize the tags
            if not audiofile.tag: audiofile.initTag()
             
            audiofile.tag.artist = metadata
            audiofile.tag.album = album
            audiofile.tag.track_num = counter+1
            # Set the front cover
            with open(image, 'rb') as cover_image: audiofile.tag.images.set(3, cover_image.read(), 'image/jpeg')
            audiofile.tag.save()

    end_time = time.time(); print(''); console.log("Finished in %i minutes" % ((end_time-start_time)/60))

# ==================================================================================================================================
def arguments():
    parser = argparse.ArgumentParser(
    description='Script for download YT music',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent(f'''Examples:
Download from a URL:
{sys.argv[0]} -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'

Read from a file:
{sys.argv[0]} -p /path/artist -m 'Artist name' -f /path/to/list.txt 

Download sections and use custom names for the songs:
{sys.argv[0]} -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -sn /path/names.txt -u 'http://www.youtube.com/example'

Download sections and use default titles from the videos:
{sys.argv[0]} -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://www.youtube.com/example' 
    '''))
    parser.add_argument('-p', '--path', type=str, default='', help='Path to save the music [Text Input]')
    parser.add_argument('-m', '--metadata', type=str, default='', help='Metadata (Artist name) [Text Input]')
    parser.add_argument('-f', '--file', type=str, default='', help='Custom urls to read [File]')
    parser.add_argument('-u', '--url', type=str, default='', help='Url to download music from [Text Input]')
    parser.add_argument('-s', '--sections', type=bool, default=False, help='Download sections [True / False] (Default is False)')
    parser.add_argument('-sf', '--sections_file', type=str, default='', help='Sections to download [File]')
    parser.add_argument('-st', '--sections_title', type=bool, default=False, help='Use the sections title [True / False] (Default is False)')
    args = parser.parse_args()

    return parser, args

# ==================================================================================================================================
def yt_dlp() -> None:
    global console
    print(colored(pyfiglet.figlet_format("Yt2music"), "blue"))
    parser, args = arguments()

    if len(sys.argv) == 1: parser.print_help(); sys.exit(0)

    if not args.path: console.print("[red][!] Not path specified"); sys.exit(1)
    elif not os.path.isdir(args.path):
        input_ = str(input(colored("[?] Directory not found, Create it? [Y/n]: ", "yellow")))
        print('')
        if input_.upper == 'Y' or input_ == '': os.makedirs(args.path, exist_ok=True)
        else: sys.exit(1)

    option = checkArguments(args.metadata, args.file, args.url, args.sections, args.sections_file, args.sections_title)
    
    if option == -1: parser.print_help(); sys.exit(1)
    elif option == 1: downloadUrls(False, args.file, args.url, args.metadata, os.path.join(args.path))
    elif option == 2: downloadUrls(True, args.file, args.url, args.metadata, os.path.join(args.path))
    elif option == 3 or option == 4: downloadSections(args.sections_file, args.url, os.path.join(args.path), args.sections_title, args.metadata)

# ==================================================================================================================================
def printNexit(message: str, status: int) -> int: global console; console.print(message); return status; sys.exit(1)
# ==================================================================================================================================

def checkArguments(metadata: str, file: str, url: str, sections: bool, sections_file: str, sections_title: bool) -> int:
    if not metadata: printNexit("[red][!] Not metadata", -1)
    elif not file and not url and not sections: printNexit("[red][!] Provide a file or url", -1)
    elif file and url: printNexit("[red][!] Can't use -f and -u together", -1)
    elif file and not url and not sections: return 1 # Download from a file
    elif url and not file and not sections: 
        if requests.head(url).status_code != 200: printNexit("[red][!] Invalid url", -1)
        else: return 2 # Download from a url
    elif sections and not url: printNexit("[red][!] Provide the url if downloading sections", -1)
    elif sections and url:
        if not sections_file: printNexit("[red][!] Provide the sections file", -1)
        elif sections_file and not sections_title: return 3 # Download sections and use custom sections names
        elif sections_file and sections_title: return 4 # Download sections and use defualt names from the video

# ==================================================================================================================================
def main() -> None:
    global console
    try: yt_dlp()
    except Exception: console.print_exception(show_locals=False)

if __name__ == '__main__': main()

