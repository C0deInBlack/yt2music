#!/usr/bin/python3

import argparse, json, os, subprocess, sys, signal, shutil, requests, textwrap, mimetypes, re, time

# sys.path.append('LIBS/lib/python3.12/site-packages')
sys.path.append('/root/.local/share/pipx/venvs/rich/lib/python3.12/site-packages')
from rich.console import Console
from rich.progress import Progress

CURRENT_NAME: str # global variable to save the name of the current downloading album

def sig_handler(sig, fram) -> None:
    global CURRENT_NAME
    try: shutil.rmtree(os.path.join(CURRENT_NAME))  # delete the current dowloading folder if CTRL-C
    except Exception as e: pass
    console = Console()
    console.log("EXITING"); sys.exit(0)

signal.signal(signal.SIGINT, sig_handler) # control-c handler function

def saveName(name: str) -> None: 
    """
    modify the name of the current downloading album through the global var
    """
    global CURRENT_NAME; CURRENT_NAME = name

def getNames(file_: str) -> tuple[list[str], list[str]]:
    """
    take the file with the urls and return two lists,
    one with the albums names and other with the total songs of each album
    """
    names: list = [] 
    total_songs: list = []
    with open(file_, 'r') as f: # file_ var is where the playlist urls are
        for i in f:
            albums_names =  subprocess.run(["yt-dlp", "--flat-playlist", "--dump-single-json", i],
                                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
            x = json.loads(albums_names.stdout)
            names.append(x['title'])
            lenght = [i['title'] for i in x['entries']] # Get each song name
            total_songs.append(len(lenght)) # Total of songs
    return names, total_songs

def createUrls(url: str, file_name: str) -> str:
    """
    create the urls file 
    """
    subprocess.run(["yt-dlp", "--flat-playlist", "-i", "--print-to-file", "url", file_name, url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True, check=True) 
    return file_name

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

def downloadUrls(use_url: bool, file: str, url: str, metadata: str, app_path: str) -> None:
    """
    download the songs reading the urls from a file 
    and add metadata and cover image
    """
    start_time = time.time()
    file_name = file if not use_url else createUrls(url, 'url.txt') # create the urls file if not provided
    
    os.makedirs(app_path, exist_ok=True) # create the directory to save the music, pass if already exist
    names, total_songs = getNames(file_name)
    album_names = [rmSpecialChracters(i) for i in names]
  
    console = Console()

    with open(file_name) as f: file = [i for i in f]
   
    index_: int = 0 
    counter_: int = 0

    with Progress() as progress:
        task = progress.add_task("Downloading", total=len(file))
        for index, link in enumerate(file):
            index_ = index
            progress.update(task, advance=1, description="Downloading %i of %i" % (index+1, len(file)))

            album_path = os.path.join(app_path, album_names[index])
            saveName(album_path)

            try: os.makedirs(album_path)
            except FileExistsError: continue
           
            # This command the the argument 'check=False' to avoid raise an error when trying to download hidden videos, just skip it
            subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality",
                            "0", "-o", "%(playlist_index)s-%(title)s.%(ext)s", "-P", os.path.join(album_path), link],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
 
            subprocess.run(["yt-dlp", "--flat-playlist", "--write-thumbnail", "-o", f"{album_names[index]}.%(ext)s", "-P", album_path, link], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # add the metadata
            for counter, song in enumerate(os.listdir(album_path)):
                counter_ = counter
                if song.endswith('.mp3'):
                    image = os.path.join(album_path, f"{album_names[index]}.jpg")
                    subprocess.check_output(
                        ["eyeD3", 
                        "--artist", metadata,
                        "--album", album_names[index],
                        "--track", str(counter+1),
                        f"--add-image={image}:FRONT_COVER",
                        os.path.join(album_path, song)])     
    if total_songs[index_] != counter_: console.log("Failed downloading %d songs in %s" % (int(total_songs[index_])-int(counter_), album_names[index_]))
    end_time = time.time(); console.log("Finished in %i seconds" % (end_time - start_time))

def downloadSections(file: str, url: str, app_path: str, sections_title: bool, metadata: str) -> None:
    """
    download sections from a video and save it as individual songs,
    the file to read must have the sections to extract in the next format: "00:00-05:10,05:10-10:00"
    or the section title if is available
    """
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
        duration = subprocess.run(["yt-dlp", "--print", "duration_string", url], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
        # Add the duration of the video in the las section
        sections_1[-1] = f"{sections_1[-1]}-{duration.stdout}"
 
    # get the name of the video and save it as album name
    album_name =  subprocess.run(["yt-dlp", "--flat-playlist", "--dump-single-json", url],stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
    x = json.loads(album_name.stdout); album = x['title']

    console = Console()
    with Progress() as progress:
        task1 = progress.add_task("Downloading", total=len(file))
        for index, section in enumerate(lines):
            progress.update(task1, advance=1, description="Downloading Section %i of %i" % (index+1, len(lines)))
            if sections_title: 
                subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", f"{index+1}-%(section_title)s.%(ext)s",
                                "-P", os.path.join(app_path), "--download-sections", f"{section}", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            else:
                subprocess.run([
                    "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", f"{index+1}-{sections_names[index]}.%(ext)s",
                    "-P", os.path.join(app_path), "--download-sections", f"*{sections_1[index]}", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) 
    
    # save the thumbnail
    subprocess.run(["yt-dlp", "--flat-playlist", "--write-thumbnail", "-o", f"{album}.%(ext)s", "-P", os.path.join(app_path), url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # convert the webp to jpg for better image quality
    subprocess.run(["magick", os.path.join(app_path, f"{album}.webp"), os.path.join(app_path, f"{album}.jpg")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
       
    # Clean the directory, remove the video file downloaded
    try: [os.remove(os.path.join(app_path, i)) for i in os.listdir(os.path.join(app_path)) if mimetypes.guess_type(i)[0].startswith('video')]
    except: pass

    # add the metadata
    for counter, song in enumerate(os.listdir(app_path)):
        if song.endswith('.mp3'):
            image = os.path.join(app_path, f"{album}.jpg")
            subprocess.check_output(
                ["eyeD3",
                 "--artist", metadata,
                "--album", album,
                "--track", str(counter+1),
                f"--add-image={image}:FRONT_COVER",
                os.path.join(app_path, song)])
    
    end_time = time.time(); console.log("Finished in %i seconds" % (end_time - start_time))

def arguments() -> list[argparse.ArgumentParser, argparse.ArgumentParser.parse_args]:
    parser = argparse.ArgumentParser(
    description='Script for download YT music',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Examples:
Download from a URL:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -u 'https://www.youtube.com/example'

Read from a file:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -f /path/to/list.txt 

Download sections and use custom names for the songs:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/file.txt -sn /path/names.txt -u 'http://www.youtube.com/example'

Download sections and use default titles from the videos:
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://www.youtube.com/example' 
        '''))
    parser.add_argument('-m', '--metadata', type=str, default='', help='Metadata (Artist name) [Text Input]')
    parser.add_argument('-f', '--file', type=str, default='', help='Custom urls to read [File]')
    parser.add_argument('-u', '--url', type=str, default='', help='Url to download music from [Text Input]')
    parser.add_argument('-s', '--sections', type=bool, default=False, help='Download sections [True / False] (Default is False)')
    parser.add_argument('-sf', '--sections_file', type=str, default='', help='Sections to download [File]')
    parser.add_argument('-st', '--sections_title', type=bool, default=False, help='Use the sections title [True / False] (Default is False)')
    args = parser.parse_args()

    return parser, args

def yt_dlp() -> None:
    parser, args = arguments()

    if len(sys.argv) == 1: parser.print_help(); sys.exit(1)

    option = checkArguments(args.metadata, args.file, args.url, args.sections, args.sections_file, args.sections_title)
    
    if option == -1: parser.print_help(); sys.exit(1)
    elif option == 1: downloadUrls(False, args.file, args.url, args.metadata, '/app/data')
    elif option == 2: downloadUrls(True, args.file, args.url, args.metadata, '/app/data')
    elif option == 3 or option == 4: downloadSections(args.sections_file, args.url, '/app/data', args.sections_title, args.metadata)

def printNexit(message: str, status: int) -> int: console = Console(); console.log(message); return status; sys.exit(1)

def checkArguments(metadata: str, file: str, url: str, sections: bool, sections_file: str, sections_title: bool) -> int:
    if not metadata: printNexit("Not metadata", -1)
    elif not file and not url and not sections: printNexit("Provide a file or url", -1)
    elif file and url: printNexit("Can't use -f and -u together", -1)
    elif file and not url and not sections: return 1 # Download from a file
    elif url and not file and not sections: 
        if requests.head(url).status_code != 200: printNexit("Invalid url", -1)
        else: return 2 # Download from a url
    elif sections and not url: printNexit("Provide the url if downloading sections", -1)
    elif sections and url:
        if not sections_file: printNexit("Provide the sections file", -1)
        elif sections_file and not sections_title: return 3 # Download sections and use custom sections names
        elif sections_file and sections_title: return 4 # Download sections and use defualt names from the video

def main() -> None: yt_dlp()

if __name__ == '__main__': main()

