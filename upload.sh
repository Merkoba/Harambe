#!/usr/bin/env bash

# This script can be used to upload files to a Harambe server
# Usage: ./upload.sh <file_path>
# Example: ./upload.sh /path/to/file.jpg

# -------------------------------

# URL="localhost:4040"
URL="https://someurl.com"
KEY="somekey"

# -------------------------------

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file_path>"
    exit 1
fi

# Resolve the full path of the file
FILE_PATH="$1"

# Remove "file://" prefix if present
if [[ "$FILE_PATH" == file://* ]]; then
    FILE_PATH="${FILE_PATH#file://}"
fi

# Convert to absolute path
FILE_PATH=$(realpath "$FILE_PATH")

if [ -z "$URL" ]; then
  echo "Error: URL is not set"
  exit 1
fi

if [ -z "$FILE_PATH" ]; then
  echo "Error: FILE_PATH is not set"
  exit 1
fi

if [ -z "$KEY" ]; then
  echo "Error: KEY is not set"
  exit 1
fi

# Prompt to get the title
title=$(zenity --entry --title="Harambe Upload" --text="Enter a title:")

# Make the POST request and capture the response
RESPONSE=$(curl -s -X POST "$URL/upload" \
    -F "file=@${FILE_PATH}" \
    -F "title=${title}" \
    -F "key=${KEY}")

# Check if the response starts with "file/"
if [[ "$RESPONSE" == post/* ]]; then
    FULL_URL="${URL}/${RESPONSE}"
    echo -n "$FULL_URL" | xclip -selection clipboard
    echo "URL Copied: $FULL_URL"
    awesome-client 'Utils.msg("Harambe: Upload Complete")'
else
    echo $RESPONSE
fi