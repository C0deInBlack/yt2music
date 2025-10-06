#!/usr/bin/bash

# if [ "$(id -u)" -ne 0 ]; then
  # echo -e "\n[!] Run as root\n"
  # exit 1
# else 

if [ "$#" -ne 3 ]; then 
    echo -e "\n[?] Usage: $BASH_SOURCE <artist> <album> <image>\n"
    exit 1
else 
    artist=$1
    album=$2
    image=$3
    counter=1
    magick "$image" -resize 640x640! "$image" > /dev/null
    while IFS= read file; do 
      for (( i = 0; i < 3; i++ )); do
        eyeD3 --artist "$artist" --album "$album" --track "$counter" --add-image="$image":FRONT_COVER "$file" > /dev/null 
      done
      ((counter++))
    done < <(/bin/ls | sort -n | grep '.mp3$' 2>/dev/null)
fi 
