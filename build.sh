#!/bin/bash    

echo "⬇ Downloading datanew.json from Google Drive..."

FILE_ID="1_qeCM87wBablojyusQe8B7-ehADjE9E-"
OUTPUT_FILE="cleaned.json"

curl -L -o "$OUTPUT_FILE" "https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo "✅ datanew.json downloaded successfully!"
