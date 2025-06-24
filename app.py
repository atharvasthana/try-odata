import json
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

# ✅ Load JSON data
with open('new.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# ✅ OData $metadata endpoint for Salesforce Connect
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


# ✅ Data endpoint with $top, $skip, $filter
@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = books

    # Optional filter parsing
    if filter_query:
        try:
            field, _, value = filter_query.partition(" eq ")
            field = field.strip()
            value = unquote(value.strip().strip("'").strip('"'))

            # OData field to JSON key mapping
            field_map = {
                "Serial": "Serial",
                "Title": "Title",
                "Author": "Author",
                "PublishDate": "PublishDate",
                "Publisher": "Publisher"
            }

            json_field = field_map.get(field)
            if json_field:
                filtered_books = [b for b in books if str(b.get(json_field, "")).strip().lower() == value.lower()]
        except Exception as e:
            print("⚠️ Filter error:", e)

    paginated = filtered_books[skip: skip + top]

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": paginated
    })


# ✅ Root
@app.route('/')
def home():
    return "✅ JSON-based OData API is live and filter-ready for Salesforce Connect!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
