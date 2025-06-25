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
gdrive_file_id = '1_qeCM87wBablojyusQe8B7-ehADjE9E-'


# === ✅ Google Drive Download Function ===
def download_cleaned_json():
    url = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    print("📥 Downloading cleaned.json from Google Drive...")

    response = session.get(url, params={'id': gdrive_file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        print("🔐 Large file detected, using confirm token...")
        response = session.get(url, params={'id': gdrive_file_id, 'confirm': token}, stream=True)

    with open(json_path, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

    print("✅ cleaned.json downloaded.")

def get_confirm_token(response):
    for k, v in response.cookies.items():
        if k.startswith('download_warning'):
            return v
    return None

# === ✅ Safe Load of JSON Data ===
def load_books():
    global books
    if not os.path.exists(json_path) or os.path.getsize(json_path) < 100000:
        try:
            download_cleaned_json()
        except Exception as e:
            print(f"❌ Failed to download JSON: {e}")
            return

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

# === ✅ OData Metadata Endpoint ===
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

# === ✅ OData EntitySet Endpoint ===
@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = books

    # Apply OData-style filter
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

# === ✅ Home Route ===
@app.route('/')
def home():
    return "✅ JSON-based OData API is live, robust, and filter-ready for Salesforce Connect!"

# === ✅ Start Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
