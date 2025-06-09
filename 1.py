from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL connection config
db_config = {
    'host': 'mysql.railway.internal',    
    'port': 3306,          # or your cloud DB host
    'user': 'root',
    'password': 'RsWYYEzfWZnaKUQNBdRtKxfLtXOhwTaj',
    'database': 'railway'            # your MySQL DB name
}

@app.route('/odata/isbn_data', methods=['GET'])
def get_isbn_data():
    limit = request.args.get('$top', 1000)  # Salesforce Connect uses $top
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM isbn_data LIMIT {limit}")
    rows = cursor.fetchall()

    response = {
        "@odata.context": "https://yourdomain.com/odata/$metadata#isbn_data",
        "value": rows
    }

    cursor.close()
    conn.close()
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

