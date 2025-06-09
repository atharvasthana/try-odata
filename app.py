from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data simulating a table called 'isbn_data'
isbn_data = [
    {"id": 1, "isbn": "978-3-16-148410-0", "title": "Book One", "author": "Author A", "year": 2020},
    {"id": 2, "isbn": "978-1-23-456789-7", "title": "Book Two", "author": "Author B", "year": 2019},
    {"id": 3, "isbn": "978-0-12-345678-9", "title": "Book Three", "author": "Author C", "year": 2021}
]

# 🔧 Remove gzip headers to avoid Salesforce Connect error
@app.after_request
def disable_compression(response: Response):
    response.headers.pop('Content-Encoding', None)
    return response

@app.route('/')
def home():
    return "API is online ✅"

# ✅ Salesforce Connect endpoint
@app.route('/odata/isbn_data', methods=['GET'])
def get_isbn_data():
    limit = int(request.args.get('$top', 1000))  # Optional: use Salesforce's $top query param
    limited_data = isbn_data[:limit]

    response = {
        "@odata.context": "https://yourdomain.com/odata/$metadata#isbn_data",  # Replace with your actual domain if needed
        "value": limited_data
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
