import os
import sqlite3
import requests
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = 'output.db'
DB_URL = 'https://drive.google.com/uc?export=download&id=1TKXgC9V8e9wuA_88uRmWL9kYuag85S1L'


# Download .db from Google Drive if not exists
if not os.path.exists(DB_PATH):
    print("📥 Downloading .db from Google Drive...")
    r = requests.get(DB_URL)
    with open(DB_PATH, 'wb') as f:
        f.write(r.content)
    print("✅ Download complete.")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="IsbnModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="importbook0_1">
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
        <EntitySet Name="importbook0_1" EntityType="IsbnModel.importbook0_1"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

@app.route('/odata/importbook0_1', methods=['GET'])
def get_isbn_data():
    top = int(request.args.get('$top', 100))
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM importbook0_1 LIMIT ?', (top,)).fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#importbook0_1",
        "value": data
    })

@app.route('/')
def home():
    return "✅ OData API is running and using .db from Google Drive!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
