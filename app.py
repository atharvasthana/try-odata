import json
import os
import requests
import ijson
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

json_path = 'cleaned.json'
mediafire_url = 'https://www.mediafire.com/file/ck09b4e20zr50ez/cleaned.json/file'

def download_from_mediafire():
    print("📥 Downloading from MediaFire...")
    try:
        session = requests.Session()
        response = session.get(mediafire_url, allow_redirects=True)

        redirect_url = response.url.replace('/file/', '/download/')
        download_page = session.get(redirect_url)
        import re
        match = re.search(r'href="(https://download[^"]+)"', download_page.text)
        if not match:
            print("❌ Failed to parse direct download URL.")
            return

        real_url = match.group(1)
        print(f"➡️ Real download URL: {real_url}")

        file_response = session.get(real_url, stream=True)
        if file_response.status_code == 200:
            with open(json_path, 'wb') as f:
                for chunk in file_response.iter_content(32768):
                    f.write(chunk)
            print("✅ cleaned.json downloaded.")
        else:
            print("❌ Download failed:", file_response.status_code)
    except Exception as e:
        print("❌ Error:", e)

# ✅ Streaming function with ijson
def stream_books():
    if not os.path.exists(json_path) or os.path.getsize(json_path) < 100000:
        download_from_mediafire()

    if not os.path.exists(json_path):
        print("❌ JSON file missing.")
        return []

    print("📂 Streaming data with ijson...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return list(ijson.items(f, 'item'))  # Top-level JSON must be a list
    except Exception as e:
        print("❌ Error streaming JSON:", e)
        return []

# No preloading to avoid memory use
@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="BookModel">
      <EntityType Name="ISBN">
        <Key><PropertyRef Name="Serial"/></Key>
        <Property Name="Serial" Type="Edm.String" Nullable="false"/>
        <Property Name="Title" Type="Edm.String"/>
        <Property Name="Author" Type="Edm.String"/>
        <Property Name="PublishDate" Type="Edm.String"/>
        <Property Name="NumberofPages" Type="Edm.Int32"/>
        <Property Name="CoverImage" Type="Edm.String"/>
        <Property Name="Publisher" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="Container">
        <EntitySet Name="ISBN" EntityType="BookModel.ISBN"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = []
    count = 0
    matched = 0

    for book in stream_books():
        if filter_query:
            try:
                field, _, value = filter_query.partition(" eq ")
                field = field.strip()
                value = unquote(value.strip().strip("'").strip('"'))

                if field in book and str(book.get(field, "")).strip().lower() != value.lower():
                    continue
            except Exception as e:
                print("⚠️ Filter error:", e)
                continue

        if matched >= skip + top:
            break
        if matched >= skip:
            filtered_books.append(book)
        matched += 1

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": filtered_books
    })

@app.route('/')
def home():
    return "✅ Streamed OData API is live — memory efficient and MediaFire ready!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
