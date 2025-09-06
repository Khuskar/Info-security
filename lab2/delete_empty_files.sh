#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: $0 directory"
  exit 1
fi

DIR=$1

if [ ! -d "$DIR" ]; then
  echo "Error: Directory not found!"
  exit 1
fi

EMPTY_FILES=$(find "$DIR" -type f -empty)

if [ -z "$EMPTY_FILES" ]; then
  echo "No empty files found in $DIR."
else
  echo "Deleting empty files:"
  for FILE in $EMPTY_FILES; do
    echo "Deleted: $FILE"
    rm "$FILE"
  done
fi

