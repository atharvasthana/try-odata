from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API is online ✅"

@app.route('/odata/isbn_data', methods=['GET'])
def get_isbn_data():
    # Static example data simulating rows from a database
    rows = [
        {"id": 1, "isbn": "978-3-16-148410-0", "title": "Book One", "author": "Author A", "year": 2020},
        {"id": 2, "isbn": "978-1-23-456789-7", "title": "Book Two", "author": "Author B", "year": 2019},
        {"id": 3, "isbn": "978-0-12-345678-9", "title": "Book Three", "author": "Author C", "year": 2021},
    ]

    response = {
        "@odata.context": "https://yourdomain.com/odata/$metadata#isbn_data",
        "value": rows
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
