import os
import sqlite3
import requests
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# File info
DB_FILE = "output.db"
GOOGLE_DRIVE_URL = "https://drive.google.com/uc?export=download&id=1TKXgC9V8e9wuA_88uRmWL9kYuag85S1L"

# Download DB from Google Drive if not already present
if not os.path.exists(DB_FILE):
    print("Downloading database from Google Drive...")
    r = requests.get(GOOGLE_DRIVE_URL)
    with open(DB_FILE, 'wb') as f:
        f.write(r.content)
    print("✅ Download complete.")

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# OData $metadata endpoint
@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="IsbnModel">
      <EntityType Name="importbook">
        <Key><PropertyRef Name="id"/></Key>
        <Property Name="id" Type="Edm.Int32" Nullable="false"/>
        <Property Name="COL 1" Type="Edm.String"/>
        <Property Name="COL 2" Type="Edm.String"/>
        <Property Name="COL 3" Type="Edm.String"/>
        <Property Name="COL 4" Type="Edm.String"/>
        <Property Name="COL 5" Type="Edm.String"/>
        <Property Name="COL 6" Type="Edm.String"/>
        <Property Name="COL 7" Type="Edm.String"/>
        <Property Name="COL 8" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="Container">
        <EntitySet Name="importbook" EntityType="IsbnModel.importbook"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

# Main OData entity endpoint
@app.route('/odata/importbook', methods=['GET'])
def get_isbn_data():
    limit = int(request.args.get('$top', 100))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM importbook LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in rows]

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#importbook",
        "value": result
    })

@app.route('/')
def home():
    return "✅ OData API is running and serving data from Google Drive!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
