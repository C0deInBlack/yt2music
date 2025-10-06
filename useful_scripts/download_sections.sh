#!/usr/bin/bash

if [ "$#" -ne 2 ]; then 
    echo -e "\n[?] Usage: $BASH_SOURCE <list> <url>\n"
    exit 1
else 
    list=$1
    url=$2
    counter=0
    while IFS= read line; do
        # yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$((counter+1))-%(section_title)s.%(ext)s" -P . --download-sections "$line" "$url"
        yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$((counter+1)).%(ext)s" -P . --download-sections "*$line" "$url"
        ((counter++))
        # echo "$line"
    done < "$list"
fi 

# yt-dlp -x --audio-format mp3 \
#        --download-sections "*00:00-05:10,*05:10-10:00,*10:00-15:38" \
#        --postprocessor-args "-ss 00:00 -to 05:10" \
#        --postprocessor-args "-ss 05:10 -to 10:00" \
#        --postprocessor-args "-ss 10:00 -to 15:38" \
#        --output "%(artist)s - %(title)s - %(section_start)s.%(ext)s" \
#        [VIDEO_URL]
#
