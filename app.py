import json
import os
import requests
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

books = []
json_path = 'cleaned.json'
mediafire_url = 'https://www.mediafire.com/file/ck09b4e20zr50ez/cleaned.json/file'


# ✅ Download cleaned.json from MediaFire
def download_from_mediafire():
    print("📥 Downloading from MediaFire...")

    try:
        session = requests.Session()
        response = session.get(mediafire_url, allow_redirects=True)
        if response.status_code != 200:
            print(f"❌ Failed to reach MediaFire page: {response.status_code}")
            return

        # Follow actual download redirect
        redirect_url = response.url.replace('/file/', '/download/')
        download_page = session.get(redirect_url)
        if 'href="' not in download_page.text:
            print("❌ Couldn't extract real download URL.")
            return

        # Extract the real file URL from the download page
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
                    if chunk:
                        f.write(chunk)
            print("✅ cleaned.json downloaded from MediaFire.")
        else:
            print(f"❌ Download failed: {file_response.status_code}")

    except Exception as e:
        print(f"❌ Exception while downloading: {e}")


# ✅ Safe JSON loader
def load_books():
    global books
    if not os.path.exists(json_path) or os.path.getsize(json_path) < 100000:
        download_from_mediafire()

    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                head = f.read(500)
                if '<html' in head.lower():
                    print("❌ cleaned.json contains HTML, not JSON.")
                    return
                f.seek(0)
                books = json.load(f)
                print(f"✅ Loaded {len(books)} book records.")
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
    else:
        print("⚠️ cleaned.json is still missing or invalid.")


load_books()


# ✅ OData $metadata endpoint
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


# ✅ OData main data endpoint
@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = books

    if filter_query:
        try:
            field, _, value = filter_query.partition(" eq ")
            field = field.strip()
            value = unquote(value.strip().strip("'").strip('"'))
            field_map = {
                "Serial": "Serial",
                "Title": "Title",
                "Author": "Author",
                "PublishDate": "PublishDate",
                "Publisher": "Publisher"
            }
            json_field = field_map.get(field)
            if json_field:
                filtered_books = [
                    b for b in books if str(b.get(json_field, "")).strip().lower() == value.lower()
                ]
        except Exception as e:
            print("⚠️ Filter error:", e)

    paginated = filtered_books[skip: skip + top]
    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": paginated
    })


# ✅ Root health check
@app.route('/')
def home():
    return "✅ JSON-based OData API is live, filter-ready, and using MediaFire as source!"

# ✅ Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
