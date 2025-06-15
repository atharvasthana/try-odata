#!/bin/bash    

echo "⬇ Downloading datanew.json from Google Drive..."

FILE_ID="1boxmDOyJdicILeN51lQfkJWZtA3eNmdl"
OUTPUT_FILE="datanew.json"

curl -L -o "$OUTPUT_FILE" "https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo "✅ datanew.json downloaded successfully!"
