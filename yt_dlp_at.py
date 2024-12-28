#!/usr/bin/python 

import subprocess, sys, argparse, os, signal, textwrap

VERSION: str = "v1.6"
# VERSION: str = "latest"
IMAGE: str = "c0deinblack/yt-dlp-at"
# IMAGE: str = "test2"

def yt_dlp() -> None:
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
./yt_dlp_at.py -p /path/artist -m 'Artist name' -s true -sf /path/sections_file.txt -st true -u 'http://ww.youtube.com/example' 
        '''))
    parser.add_argument('-p', '--path', type=str, default='', help='Path to save the music [Text Input]')
    parser.add_argument('-m', '--metadata', type=str, default='', help='Metadata (Artist name) [Text Input]')
    parser.add_argument('-f', '--file', type=str, default='', help='Custom urls to read [File]')
    parser.add_argument('-u', '--url', type=str, default='', help='Url to download music from [Text Input]')
    parser.add_argument('-s', '--sections', type=bool, default=False, help='Download sections [True / False] (Default is False)')
    parser.add_argument('-sf', '--sections_file', type=str, default='', help='Sections to download [File]')
    parser.add_argument('-sn', '--sections_names', type=str, default='', help='Names of the sections [File]')
    parser.add_argument('-st', '--sections_title', type=bool, default=False, help='Use the sections title [True / False] (Default is False)')
    args = parser.parse_args()

    command: str = ["docker", "run", "-it", "--rm"]
    parameters: str = []

    if not args.path: parser.print_help(); sys.exit(1)
    elif not os.path.isdir(args.path):
        input_ = str(input("[?] Directory not found, Create it? [Y/n]: "))
        if input_.upper == 'Y' or input_ == '': os.makedirs(args.path, exist_ok=True)
        else: sys.exit(1)
        
    if args.path: command.append("-v"); command.append(f"{args.path}:/app/data")
    if args.metadata: parameters.append("-m"); parameters.append(args.metadata)
    if args.file:
        command.append("-v"); command.append(f"{args.file}:/app/{os.path.basename(args.file)}")
        parameters.append("-f"); parameters.append(os.path.basename(args.file))
    if args.url: parameters.append("-u"); parameters.append(args.url)
    if args.sections: parameters.append("-s"); parameters.append("true")
    if args.sections_file:
        command.append("-v"); command.append(f"{args.sections_file}:/app/{os.path.basename(args.sections_file)}")
        parameters.append("-sf"); parameters.append(os.path.basename(args.sections_file))
    if args.sections_names:
        command.append("-v"); command.append(f"{args.sections_names}:/app/{os.path.basename(args.sections_names)}")
        parameters.append("-sn"); parameters.append(os.path.basename(args.sections_names))
    if args.sections_title: parameters.append("-st"); parameters.append("true")
    
    command.append(f"{IMAGE}:{VERSION}")

    command.extend(parameters)
    subprocess.run(command, text=True, check=True) 

def main() -> None: yt_dlp()

if __name__ == '__main__': main()
