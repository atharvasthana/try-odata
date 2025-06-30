import os
import re
import json
import requests
import ijson
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

CHUNK_URLS = {
    0: "https://www.mediafire.com/file/5p3ur2ksl1dp9vj/chunk_0.json/file",
    1: "https://www.mediafire.com/file/ge96n79t7pjefq4/chunk_1.json/file",
    2: "https://www.mediafire.com/file/mhnrtbeqt26581x/chunk_2.json/file",
    3: "https://www.mediafire.com/file/3xep7y05auqc119/chunk_3.json/file",
    4: "https://www.mediafire.com/file/msh9usn8p5s2cj3/chunk_4.json/file",
    5: "https://www.mediafire.com/file/iqxtzapklfsfqwm/chunk_5.json/file",
    6: "https://www.mediafire.com/file/ac6jvxkly1fbbfg/chunk_6.json/file",
    7: "https://www.mediafire.com/file/f5t63vd6ynq2oew/chunk_7.json/file",
    8: "https://www.mediafire.com/file/fzqo4tx8t0hh9qo/chunk_8.json/file",
    9: "https://www.mediafire.com/file/kka2yq2wgciq2no/chunk_9.json/file",
    10: "https://www.mediafire.com/file/9cxfpleb4re2nvn/chunk_10.json/file"
}

CHUNK_FOLDER = 'chunks'
INDEX_FOLDER = 'indexes'
os.makedirs(CHUNK_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

INDEX_FILES = {
    "Serial": "https://www.mediafire.com/file/zs38nlhv3xzk5td/serial_index.json/file",
    "Title": "https://www.mediafire.com/file/sqajng20pv8d8rc/title_index.json/file"
}

def get_chunk_path(chunk_id):
    return os.path.join(CHUNK_FOLDER, f'chunk_{chunk_id}.json')

def get_index_path(field):
    return os.path.join(INDEX_FOLDER, f'index_{field.lower()}.json')

def download_file(url, path):
    try:
        session = requests.Session()
        response = session.get(url, allow_redirects=True)
        redirect_url = response.url.replace('/file/', '/download/')
        download_page = session.get(redirect_url)
        match = re.search(r'href="(https://download[^"]+)"', download_page.text)

        if not match:
            print(f"❌ Failed to parse download URL for {url}")
            return False
        real_url = match.group(1)
        r = session.get(real_url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(32768):
                    f.write(chunk)
            print(f"✅ Downloaded: {path}")
            return True
    except Exception as e:
        print(f"❌ Download failed for {url}: {e}")
    return False

def load_index(field):
    if field not in INDEX_FILES:
        return {}
    path = get_index_path(field)
    if not os.path.exists(path):
        download_file(INDEX_FILES[field], path)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = []
    matched = 0

    field_map = {
        "Serial": "Serial",
        "Title": "Title"
    }

    filter_field = filter_value = None
    chunks_to_search = list(CHUNK_URLS)

    if filter_query:
        try:
            raw_field, _, raw_value = filter_query.partition(" eq ")
            filter_field = field_map.get(raw_field.strip())
            filter_value = unquote(raw_value.strip("'").strip('"')).lower()

            index_data = load_index(filter_field)
            chunks_to_search = index_data.get(filter_value, [])
        except Exception as e:
            print("⚠️ Filter parse error:", e)

    for chunk_id in chunks_to_search:
        chunk_path = get_chunk_path(chunk_id)
        if not os.path.exists(chunk_path):
            download_file(CHUNK_URLS[chunk_id], chunk_path)
        if not os.path.exists(chunk_path):
            continue

        with open(chunk_path, 'r', encoding='utf-8') as f:
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
        if matched >= skip + top:
            break

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": filtered_books
    })

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

@app.route('/')
def home():
    return "✅ OData API is live with on-demand index loading!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
