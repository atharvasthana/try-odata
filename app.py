import os
import re
import requests
import ijson
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

CHUNK_URLS = {
    0: "https://www.mediafire.com/file/5p3ur2ksl1dp9vj/chunk_0.json/file",
    1: "https://www.mediafire.com/file/ge96n79t7pjefq4/chunk_1.json/file",
    2: "https://www.mediafire.com/file/mhnrtbeqt26581x/chunk_2.json/file",
    3: "https://www.mediafire.com/file/3xep7y05auqc119/chunk_3.json/file",
    4: "https://www.mediafire.com/file/msh9usn8p5s2cj3/chunk_4.json/file",
    5: "https://www.mediafire.com/file/iqxtzapklfsfqwm/chunk_5.json/file",
    6: "https://www.mediafire.com/file/ac6jvxkly1fbbfg/chunk_6.json/file",
    7: "https://www.mediafire.com/file/f5t63vd6ynq2oew/chunk_7.json/file",
    8: "https://www.mediafire.com/file/fzqo4tx8t0hh9qo/chunk_8.json/file",
    9: "https://www.mediafire.com/file/kka2yq2wgciq2no/chunk_9.json/file",
    10: "https://www.mediafire.com/file/9cxfpleb4re2nvn/chunk_10.json/file",
    11: "https://www.mediafire.com/file/1yw16st18am50zv/chunk_11.json/file",
    12: "https://www.mediafire.com/file/fpz50zqrf5jy5fx/chunk_12.json/file",
    13: "https://www.mediafire.com/file/pptusgxwtk6pm2b/chunk_13.json/file",
    14: "https://www.mediafire.com/file/bh4qc1guu01st8l/chunk_14.json/file",
    15: "https://www.mediafire.com/file/uj7kkbio91birjn/chunk_15.json/file",
    16: "https://www.mediafire.com/file/rovn3bgl6g2gv6j/chunk_16.json/file",
    17: "https://www.mediafire.com/file/20wk2xdiq96wbz2/chunk_17.json/file",
    18: "https://www.mediafire.com/file/jupnl440559d40f/chunk_18.json/file",
    19: "https://www.mediafire.com/file/axwf6k8kvbbz1hf/chunk_19.json/file",
    20: "https://www.mediafire.com/file/5z0c34y941z0i9z/chunk_20.json/file",
    21: "https://www.mediafire.com/file/u0n8nzpp1swrxuz/chunk_21.json/file",
    22: "https://www.mediafire.com/file/xoltc4jgea6hoqj/chunk_22.json/file",
    23: "https://www.mediafire.com/file/lnkw8gny8frt7lz/chunk_23.json/file",
    24: "https://www.mediafire.com/file/on8w7036f70hg91/chunk_24.json/file",
    25: "https://www.mediafire.com/file/vaz2b0wtcdyw00w/chunk_25.json/file",
    26: "https://www.mediafire.com/file/cbhygtgv4syvg99/chunk_26.json/file",
    27: "https://www.mediafire.com/file/jo2foug759rtfho/chunk_27.json/file",
    28: "https://www.mediafire.com/file/jm676deg83y44e9/chunk_28.json/file",
    29: "https://www.mediafire.com/file/zasrvvl9f218kt4/chunk_29.json/file",
    30: "https://www.mediafire.com/file/vfqrqm5wzdyhc6a/chunk_30.json/file",
    31: "https://www.mediafire.com/file/2z7f38c2ihfjgyu/chunk_31.json/file",
    32: "https://www.mediafire.com/file/g67dz5zpwnk9mee/chunk_32.json/file",
    33: "https://www.mediafire.com/file/a45efqtmabig01w/chunk_33.json/file",
    34: "https://www.mediafire.com/file/7s0iychvgld2n6t/chunk_34.json/file",
    35: "https://www.mediafire.com/file/pq86ks07fdtdrzh/chunk_35.json/file",
    36: "https://www.mediafire.com/file/s57d12eph0pqaxa/chunk_36.json/file",
    37: "https://www.mediafire.com/file/wfcj3w17zk655w7/chunk_37.json/file",
    38: "https://www.mediafire.com/file/altwvg6y5aqaefa/chunk_38.json/file",
    39: "https://www.mediafire.com/file/h1eh39fu1wuy19k/chunk_39.json/file",
    40: "https://www.mediafire.com/file/x2pcuia3fsi1ybl/chunk_40.json/file"
}

CHUNK_FOLDER = 'chunks'
os.makedirs(CHUNK_FOLDER, exist_ok=True)


# --- ✅ Local Disk Caching with Fast Lookup Map ---
INDEX_MAP = {}
INDEX_FIELDS = ["Serial", "Title"]  # Can expand to Author, etc.


def get_chunk_path(chunk_id):
    return os.path.join(CHUNK_FOLDER, f'chunk_{chunk_id}.json')


def download_chunk(chunk_id):
    if chunk_id not in CHUNK_URLS:
        print(f"❌ No URL for chunk {chunk_id}")
        return False

    url = CHUNK_URLS[chunk_id]
    try:
        session = requests.Session()
        print(f"📥 Downloading chunk {chunk_id} from MediaFire...")
        response = session.get(url, allow_redirects=True)
        redirect_url = response.url.replace('/file/', '/download/')
        download_page = session.get(redirect_url)

        match = re.search(r'href="(https://download[^"]+)"', download_page.text)
        if not match:
            print("❌ Failed to parse real download URL.")
            return False

        real_url = match.group(1)
        print(f"➡️ Chunk {chunk_id} real URL: {real_url}")

        file_response = session.get(real_url, stream=True)
        if file_response.status_code == 200:
            with open(get_chunk_path(chunk_id), 'wb') as f:
                for chunk in file_response.iter_content(32768):
                    f.write(chunk)
            print(f"✅ chunk_{chunk_id}.json downloaded.")
            return True
    except Exception as e:
        print(f"❌ Chunk {chunk_id} download failed:", e)
    return False


# --- ✅ Preload Index Map ---
def build_index():
    global INDEX_MAP
    print("🔍 Building index...")
    for chunk_id in CHUNK_URLS:
        chunk_path = get_chunk_path(chunk_id)
        if not os.path.exists(chunk_path):
            download_chunk(chunk_id)

        if not os.path.exists(chunk_path):
            continue

        with open(chunk_path, 'r', encoding='utf-8') as f:
            for book in ijson.items(f, 'item'):
                for field in INDEX_FIELDS:
                    value = book.get(field)
                    if value:
                        key = str(value).strip().lower()
                        INDEX_MAP.setdefault(field, {}).setdefault(key, []).append(chunk_id)
    print("✅ Index built!")


@app.route('/odata/ISBN')
def get_books():
    top = int(request.args.get('$top', 100))
    skip = int(request.args.get('$skip', 0))
    filter_query = request.args.get('$filter')

    filtered_books = []
    matched = 0

    field_map = {
        "Serial": "Serial",
        "Title": "Title",
        "Author": "Author",
        "PublishDate": "PublishDate",
        "Publisher": "Publisher"
    }

    filter_field = filter_value = None
    chunks_to_search = list(CHUNK_URLS)

    if filter_query:
        try:
            raw_field, _, raw_value = filter_query.partition(" eq ")
            filter_field = field_map.get(raw_field.strip())
            filter_value = unquote(raw_value.strip().strip("'").strip('"')).lower()

            if filter_field in INDEX_MAP:
                chunks_to_search = INDEX_MAP.get(filter_field, {}).get(filter_value, [])
        except Exception as e:
            print("⚠️ Filter parse error:", e)

    for chunk_id in chunks_to_search:
        chunk_path = get_chunk_path(chunk_id)
        if not os.path.exists(chunk_path):
            download_chunk(chunk_id)

        if not os.path.exists(chunk_path):
            continue

        with open(chunk_path, 'r', encoding='utf-8') as f:
            for book in ijson.items(f, 'item'):
                if filter_field and filter_field in book:
                    value = str(book.get(filter_field, "")).strip().lower()
                    if value != filter_value:
                        continue

                if matched >= skip + top:
                    break
                if matched >= skip:
                    filtered_books.append(book)
                matched += 1

        if matched >= skip + top:
            break

    return jsonify({
        "@odata.context": request.url_root.rstrip('/') + "/odata/$metadata#ISBN",
        "value": filtered_books
    })


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


@app.route('/')
def home():
    return "✅ Multi-chunk OData API is live — MediaFire-backed, filterable & efficient!"


if __name__ == '__main__':
    build_index()
    app.run(host='0.0.0.0', port=10000)
