#!/bin/bash

echo "⬇ Downloading books.json from Google Drive..."

FILE_ID="15qWEjGpHmzVWzIaQwy8AgUOqRAV38kxr"
OUTPUT_FILE="books.json"

curl -L -o "$OUTPUT_FILE" "https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo "✅ books.json downloaded successfully!"
