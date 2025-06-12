import sqlite3
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "output.db"  # Already downloaded during build by build.sh

# Connect to SQLite DB
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="IsbnModel">
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

@app.route('/odata/importbook0_1')
def get_isbn_data():
    top = int(request.args.get('$top', 100))  # Default to 100 records
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM importbook0_1 LIMIT ?", (top,))
    rows = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in rows]

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#importbook0_1",
        "value": result
    })

@app.route('/')
def home():
    return "✅ OData API is running using output.db from Google Drive (fetched during build.sh)!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
