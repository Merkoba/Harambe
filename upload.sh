#!/usr/bin/env bash

# This script can be used to upload files to a Harambe server
# Usage: ./upload.sh <file_path>
# Example: ./upload.sh /path/to/file.jpg

# -------------------------------

URL="https://someurl.com"
USERNAME="someusername"
PASSWORD="somepassword"

# -------------------------------

# Resolve the full path of the file
FILE_PATH="$1"

# Prompt for title or not
MODE="${2:-normal}"

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

if [ -z "$USERNAME" ]; then
  echo "Error: USERNAME is not set"
  exit 1
fi

if [ -z "$PASSWORD" ]; then
  echo "Error: PASSWORD is not set"
  exit 1
fi

# Prompt to get the title
if [ "$MODE" == "title" ]; then
  title=$(zenity --entry --title="Harambe Upload" --text="Enter a title:")
else
  title=""
fi

if [ -n "$title" ]; then
  title_param="-F \"title=${title}\""
else
  title_param=""
fi

echo "Uploading: $FILE_PATH"

# Make the POST request and capture the response
RESPONSE=$(curl -s -X POST "$URL/upload" \
    $title_param \
    -F "file=@\"${FILE_PATH}\"" \
    -F "username=\"${USERNAME}\"" \
    -F "password=\"${PASSWORD}\"" \
)

# Check if the response starts with "file/"
if [[ "$RESPONSE" == post/* ]]; then
    FULL_URL="${URL}/${RESPONSE}"
    echo -n "$FULL_URL" | xclip -selection clipboard
    echo "URL Copied: $FULL_URL"
    awesome-client 'Utils.msg("Harambe: Upload Complete")'
else
    echo $RESPONSE
fi