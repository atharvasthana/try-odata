import json
import os
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

# === ✅ Safe JSON Load ===
books = []
json_path = 'cleaned.json'

if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
    with open(json_path, 'r', encoding='utf-8') as f:
        head = f.read(500)
        if '<html' in head.lower():
            print("❌ cleaned.json contains HTML, not JSON.")
        else:
            try:
                f.seek(0)
                books = json.load(f)
                print(f"✅ Loaded {len(books)} book records from cleaned.json")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
else:
    print("⚠️ cleaned.json is missing or empty.")

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

# === ✅ OData EntitySet Endpoint ===
@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = books

    # Apply filter if present
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

# === ✅ Root Route ===
@app.route('/')
def home():
    return "✅ JSON-based OData API is live and filter-ready for Salesforce Connect!"

# === ✅ Start App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
