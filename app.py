import json
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Load books.json data
with open('books.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# ✅ $metadata endpoint
@app.route('/odata/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="BookModel">
      <EntityType Name="ISBN_IDB__c">
        <Key><PropertyRef Name="Name"/></Key>
        <Property Name="Name" Type="Edm.String" Nullable="false"/>
        <Property Name="Title__c" Type="Edm.String"/>
        <Property Name="Author__c" Type="Edm.String"/>
        <Property Name="Publish_Date__c" Type="Edm.Date"/>
        <Property Name="Number_of_Pages__c" Type="Edm.Int32"/>
        <Property Name="Cover_Image__c" Type="Edm.String"/>
        <Property Name="Publisher__c" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="Container">
        <EntitySet Name="ISBN_IDB__c" EntityType="BookModel.ISBN_IDB__c"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

# ✅ Data endpoint
@app.route('/odata/ISBN_IDB__c')
def get_books():
    top = int(request.args.get('$top', 100))
    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN_IDB__c",
        "value": books[:top]
    })

# ✅ Root check
@app.route('/')
def home():
    return "✅ JSON-based OData API is live for Salesforce Connect!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
