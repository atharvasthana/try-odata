#!/bin/bash    

echo "⬇ Downloading books.json from Google Drive..."

FILE_ID="1sE1K-wb9h6XVMXqC55oVhLkKUGNOuISf"
OUTPUT_FILE="datanew.json"

curl -L -o "$OUTPUT_FILE" "https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo "✅ books.json downloaded successfully!"
