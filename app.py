import json
import os
import re
import requests
import ijson
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

json_path = 'cleaned.json'
mediafire_url = 'https://www.mediafire.com/file/ck09b4e20zr50ez/cleaned.json/file'

# === ✅ Download from MediaFire ===
def download_from_mediafire():
    print("📥 Downloading from MediaFire...")
    try:
        session = requests.Session()
        response = session.get(mediafire_url, allow_redirects=True)

        redirect_url = response.url.replace('/file/', '/download/')
        download_page = session.get(redirect_url)

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
        print("❌ MediaFire Error:", e)

# === ✅ OData Metadata ===
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

# === ✅ OData Entity Endpoint ===
@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    if not os.path.exists(json_path) or os.path.getsize(json_path) < 100000:
        download_from_mediafire()

    if not os.path.exists(json_path):
        return jsonify({"error": "JSON file not available"}), 500

    filtered_books = []
    matched = 0

    # Field mapping (OData to JSON keys)
    field_map = {
        "Serial": "Serial",
        "Title": "Title",
        "Author": "Author",
        "PublishDate": "PublishDate",
        "Publisher": "Publisher"
    }

    filter_field = filter_value = None
    if filter_query:
        try:
            raw_field, _, raw_value = filter_query.partition(" eq ")
            filter_field = field_map.get(raw_field.strip())
            filter_value = unquote(raw_value.strip().strip("'").strip('"')).lower()
        except Exception as e:
            print("⚠️ Filter parse error:", e)

    with open(json_path, 'r', encoding='utf-8') as f:
        for book in ijson.items(f, 'item'):
            if filter_field and filter_field in book:
                value = str(book.get(filter_field, "")).strip().lower()
                if value != filter_value:
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
    return "✅ OData API (Streaming, Filterable, MediaFire-backed) is Live!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
