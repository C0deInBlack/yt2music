#!/usr/bin/python 

import argparse, os, re, sys, datetime
sys.path.append("../LIBS/lib/python3.13/site-packages/")
from termcolor import colored
import moviepy as mp

def converter(video: str, file: str, path: str) -> None:
    with open(file) as f: lines = f.readlines() # Open the file and save it in a list

    video_mp = mp.VideoFileClip(video)

    # Search for minutes expression 00:00
    sections_1 = [re.search(r'[\d]{2}:[\d]{2}', i).group() for i in lines]
    # Search for hours expression 00:00:00
    sections_2 = [re.search(r'[\d]{2}:[\d]{2}:[\d]{2}', i) for i in lines]
    # Replace hour expression in the original list
    sections_1 = [exp.group() if exp else org for org, exp in zip(sections_1, sections_2)]
    # Create a names list replacing the time expression 
    sections_names = [line.replace(reg, '').strip() for line, reg in zip(lines, sections_1)]
    
    # Replace the list with the proper start and end time expression 00:00-00:00
    sections_1 = [f"{sections_1[i]}-{sections_1[i+1]}" if i+1 < len(sections_1) else sections_1[i] for i in range(len(sections_1))]

    end_time = str(datetime.timedelta(seconds = video_mp.duration)).split(':')[1:3]

    sections_1[-1] = f"{sections_1[-1]}-{end_time[0]}:{end_time[1]}"

    counter: int = 1
    for name, section in zip(sections_names, sections_1):
        # Format time 00:00-02:30 to seconds 0.0, 150.0
        if section.count(':') == 2:
            section_formated = [float(i.split(':')[0])*60+float(i.split(':')[1]) for i in section.split('-')]
        elif section.count(':') == 4:
            section_formated = [float(i.split(':')[0])*3600+float(i.split(':')[1])*60+float(i.split(':')[2]) for i in section.split('-')]

        clip = video_mp.subclipped(section_formated[0], section_formated[1])
        clip.audio.write_audiofile(os.path.join(path, f"{counter}-{name}.mp3"))
        counter+=1

    print(colored(f"[*] Finished, go and check {path}", "green"))

def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sections', type=str, default='', help='Sections file')
    parser.add_argument('-v', '--video', type=str, default='', help='Video file')
    parser.add_argument('-p', '--path', type=str, default='', help='Path to save mp3 files')
    args = parser.parse_args()

    return parser, args 

if __name__ == '__main__':
    parser, args = arguments()

    if len(sys.argv) == 1: parser.print_help(); sys.exit(0)
    elif not args.sections or not args.video: parser.print_help(); sys.exit(0)
    elif not os.path.isfile(args.sections) or not os.path.isfile(args.video) or not os.path.isdir(args.path): print(colored("[!] File or Video not found", "red")); exit(1)
    else: converter(args.video, args.sections, args.path)

