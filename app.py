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
    # your existing logic…

@app.route('/test_connection')
def test_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        # test query…
        return {"success": True, "timestamp": str(result[0])}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
