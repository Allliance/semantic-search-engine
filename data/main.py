from flask import Flask, request, jsonify
import json
from index import Index
from encoder import Encoder
from product import Product

app = Flask(__name__)

# Global variables for our service
index = None
encoder = None

def initialize_service(index_name='products-index', dimension=512):
    global index, encoder
    index = Index(index_name, dimension)
    encoder = Encoder()
    print("Service initialized successfully")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/index_products', methods=['POST'])
def index_products_endpoint():
    try:
        data = request.get_json()
        products_file = data.get('products_file', 'products_1.json')
        limit = data.get('limit', -1)

        with open(products_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        if limit > 0:
            products_data = products_data[:limit]

        products = [Product(product_data) for product_data in products_data]
        
        for product in products:
            image_ids = [f"{product.id}#{image_url}" for image_url in product.image_urls]
            existing_ids = index.get_by_id(image_ids)
            
            to_be_added_images = []
            to_be_added_image_ids = []
            
            for i, image_url in enumerate(product.image_urls):
                if image_ids[i] in existing_ids:
                    continue
                image = product.fetch_image(image_url)
                to_be_added_images.append(image)
                to_be_added_image_ids.append(image_ids[i])
            
            if len(to_be_added_images) == 0:
                continue

            embeddings = encoder.encode_image(to_be_added_images)
            embeddings_dict = []
            for i, embedding in enumerate(embeddings):
                embeddings_dict.append({
                    'id': to_be_added_image_ids[i],
                    'embedding': embedding,
                    'metadata': product.meta_data
                })
                
            index.upsert_embeddings(embeddings_dict)

        return jsonify({"message": "Products indexed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_endpoint():
    try:
        data = request.get_json()
        query_text = data.get('query')
        
        if not query_text:
            return jsonify({"error": "Query text is required"}), 400

        query_embedding = encoder.encode_text(query_text)
        response = index.query(query_embedding)
        
        return jsonify({"results": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_service()
    app.run(host='0.0.0.0', port=5000)
