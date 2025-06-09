from flask import Flask, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample static data for "orders"
orders = [
    {"OrderID": 1, "Customer": "Alice", "Amount": 100.50},
    {"OrderID": 2, "Customer": "Bob",   "Amount": 200.75},
    {"OrderID": 3, "Customer": "Carol", "Amount": 150.00}
]

# 1️⃣ Metadata endpoint for OData 4.0
@app.route('/orders.svc/$metadata')
def metadata():
    xml = '''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0"
    xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="OrdersModel" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="Orders">
        <Key><PropertyRef Name="OrderID"/></Key>
        <Property Name="OrderID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Customer" Type="Edm.String"/>
        <Property Name="Amount" Type="Edm.Double"/>
      </EntityType>
      <EntityContainer Name="Container">
        <EntitySet Name="Orders" EntityType="OrdersModel.Orders"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''
    return Response(xml, mimetype='application/xml')

# 2️⃣ Entity endpoint returning JSON in OData format
@app.route('/orders.svc/Orders', methods=['GET'])
def get_orders():
    # Support OData $top parameter for batching
    limit = int(request.args.get('$top', len(orders)))
    data = orders[:limit]
    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + '/orders.svc/$metadata#Orders',
        "value": data
    })

@app.route('/')
def home():
    return "OData service up and running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
