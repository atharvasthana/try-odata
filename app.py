import os
import re
import sqlite3
import requests
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

DB_PATH = 'books.db'
MEDIAFIRE_URL = "https://www.mediafire.com/file/z28tvate66crxmh/books.db/file"
  # ✅ Replace with your actual MediaFire link

def download_db_if_missing():
    if os.path.exists(DB_PATH):
        return
    print("📥 Downloading books.db from MediaFire...")

    try:
        session = requests.Session()
        page = session.get(MEDIAFIRE_URL)
        direct_link_url = page.url.replace("/file/", "/download/")
        download_page = session.get(direct_link_url)
        match = re.search(r'href="(https://download[^"]+)"', download_page.text)

        if not match:
            raise Exception("❌ Could not find direct download link.")

        real_url = match.group(1)
        r = session.get(real_url, stream=True)
        if r.status_code == 200:
            with open(DB_PATH, 'wb') as f:
                for chunk in r.iter_content(32768):
                    f.write(chunk)
            print("✅ books.db downloaded successfully.")
        else:
            raise Exception(f"❌ Download failed: {r.status_code}")
    except Exception as e:
        print(f"🔥 Failed to download books.db: {e}")
        exit(1)

def query_books(filter_field=None, filter_value=None, skip=0, top=100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM isbn"
    params = []

    if filter_field and filter_value:
        query += f" WHERE LOWER({filter_field}) = ?"
        params.append(filter_value.lower())

    query += " LIMIT ? OFFSET ?"
    params.extend([top, skip])
    cur.execute(query, params)

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    field_map = {
        "Serial": "Serial",
        "Title": "Title",
        "Author": "Author",
        "Publisher": "Publisher"
    }

    filter_field = filter_value = None
    if filter_query:
        try:
            raw_field, _, raw_value = filter_query.partition(" eq ")
            filter_field = field_map.get(raw_field.strip())
            filter_value = unquote(raw_value.strip("'").strip('"'))
        except Exception as e:
            print("⚠️ Filter parse error:", e)

    result = query_books(filter_field, filter_value, skip, top)

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": result
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
        <Property Name="NumberofPages" Type="Edm.String"/>
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
    return "✅ SQLite OData API with MediaFire auto-download is live!"

if __name__ == '__main__':
    download_db_if_missing()
    app.run(host='0.0.0.0', port=10000)
