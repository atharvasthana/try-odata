from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'mysql.railway.internal',
    'port': 3306,
    'user': 'root',
    'password': 'RsWYYEzfWZnaKUQNBdRtKxfLtXOhwTaj',
    'database': 'railway'
}

@app.route('/')
def home():
    return "API is online ✅"

@app.route('/odata/isbn_data', methods=['GET'])
def get_isbn_data():
    limit = request.args.get('$top', 1000)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM isbn_data LIMIT {limit}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        response = {
            "@odata.context": "https://yourdomain.com/odata/$metadata#isbn_data",
            "value": rows
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_connection')
def test_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"success": True, "timestamp": str(result[0])}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
