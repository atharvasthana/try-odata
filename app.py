from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample static data (replace with real DB data later if needed)
isbn_data = [
    {"id": 1, "title": "Book One", "author": "Author A", "isbn": "978-3-16-148410-0", "year": 2020},
    {"id": 2, "title": "Book Two", "author": "Author B", "isbn": "978-1-23-456789-7", "year": 2019},
    {"id": 3, "title": "Book Three", "author": "Author C", "isbn": "978-0-12-345678-9", "year": 2021}
]

# 1️⃣ OData $metadata endpoint
@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0"
    xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="IsbnModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="isbn_data">
        <Key><PropertyRef Name="id"/></Key>
        <Property Name="id" Type="Edm.Int32" Nullable="false"/>
        <Property Name="title" Type="Edm.String"/>
        <Property Name="author" Type="Edm.String"/>
        <Property Name="isbn" Type="Edm.String"/>
        <Property Name="year" Type="Edm.Int32"/>
      </EntityType>
      <EntityContainer Name="Container">
        <EntitySet Name="isbn_data" EntityType="IsbnModel.isbn_data"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

# 2️⃣ Entity endpoint
@app.route('/odata/isbn_data', methods=['GET'])
def get_isbn_data():
    limit = int(request.args.get('$top', len(isbn_data)))
    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#isbn_data",
        "value": isbn_data[:limit]
    })

# Optional root
@app.route('/')
def home():
    return "📚 OData API for isbn_data is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
