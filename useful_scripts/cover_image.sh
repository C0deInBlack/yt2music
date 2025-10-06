#!/usr/bin/bash 

# eyeD3 --add-image="$image":FRONT_COVER "$file"

if [ "$#" -ne 1 ]; then 
  echo -e "\n[?] Usage: $BASH_SOURCE <image>\n"
  exit 1;
else 
  image=$1
  magick "$image" -resize 640x640! "$image"
  while IFS= read -r file; do 
    for (( i = 0; i < 3; i++ )); do 
      eyeD3 --add-image="$image":FRONT_COVER "$file" > /dev/null 
    done
  done < <(find . -name "*.mp3" -type f 2>/dev/null)
fi
