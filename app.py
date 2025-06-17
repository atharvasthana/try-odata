import json
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load JSON data
with open('datanew.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="BookModel">
      <EntityType Name="ISBN">
        <Key><PropertyRef Name="Serial"/></Key>
        <Property Name="Serial" Type="Edm.Int32" Nullable="false"/>
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

@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_param = request.args.get('$filter')

    filtered_books = books

    if filter_param:
        try:
            # Basic support for filters like: Title eq 'xyz' AND Author eq 'abc'
            conditions = [cond.strip() for cond in filter_param.split('and')]
            for condition in conditions:
                field, op, value = condition.split(' ', 2)
                field = field.strip()
                op = op.strip()
                value = value.strip().strip("'")

                if op == 'eq':
                    if field == "Serial" or field == "NumberofPages":
                        value = int(value)
                    filtered_books = [b for b in filtered_books if str(b.get(field)) == str(value)]

        except Exception as e:
            print("⚠️ Filter parse error:", e)

    paginated = filtered_books[skip: skip + top]

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": paginated
    })

@app.route('/')
def home():
    return "✅ JSON-based OData API with multi-field filter support is live!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
