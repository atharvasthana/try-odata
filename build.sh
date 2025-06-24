#!/bin/bash    

echo "⬇ Downloading datanew.json from Google Drive..."

FILE_ID="1TLfdL0UDn9FNa0onbLSAH2oB7e5teQ-8"
OUTPUT_FILE="new.json"

curl -L -o "$OUTPUT_FILE" "https://drive.google.com/uc?export=download&id=${FILE_ID}"

echo "✅ datanew.json downloaded successfully!"
