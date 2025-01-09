import json
from index import Index
from encoder import Encoder
from product import Product
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Get configuration from environment variables
INDEX_NAME = os.getenv('INDEX_NAME', 'products-index')
DIMENSION = int(os.getenv('DIMENSION', '512'))
PRODUCTS_FILE = os.getenv('PRODUCTS_FILE', 'products_1.json')
LIMIT = int(os.getenv('LIMIT', '-1'))
VERBOSE = os.getenv('VERBOSE', 'false').lower() == 'true'

# Global variables for our service
index = None
encoder = None

def initialize_service():
    global index, encoder
    index = Index(INDEX_NAME, DIMENSION)
    encoder = Encoder()
    print("Service initialized successfully")

def index_single_product(product_data):
    """Index a single product from its JSON data"""
    global index, encoder
    
    try:
        product = Product(product_data)
        
        # Check for existing images
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
            if VERBOSE:
                print(f"Product {product.id} already exists in the index")
            return {"message": f"Product {product.id} already exists in the index"}

        embeddings = encoder.encode_image(to_be_added_images)
        embeddings_dict = []
        for i, embedding in enumerate(embeddings):
            embeddings_dict.append({
                'id': to_be_added_image_ids[i],
                'embedding': embedding,
                'metadata': product.meta_data
            })
            
        index.upsert_embeddings(embeddings_dict)
        
        if VERBOSE:
            print(f"Product {product.id} added to the index")
        
        return {"message": f"Product {product.id} successfully indexed"}
    
    except Exception as e:
        raise Exception(f"Error indexing product: {str(e)}")

def index_products():
    """Index products from the initial products file"""
    print(f"Starting indexing with parameters:")
    print(f"Index name: {INDEX_NAME}")
    print(f"Dimension: {DIMENSION}")
    print(f"Products file: {PRODUCTS_FILE}")
    print(f"Limit: {LIMIT}")
    print(f"Verbose: {VERBOSE}")

    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    if LIMIT > 0:
        products_data = products_data[:LIMIT]

    for product_data in products_data:
        try:
            result = index_single_product(product_data)
            if VERBOSE:
                print(result["message"])
        except Exception as e:
            print(f"Error indexing product: {str(e)}")
            continue

    print("Initial product indexing completed")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/index_product', methods=['POST'])
def index_product_endpoint():
    try:
        product_data = request.get_json()
        
        if not product_data:
            return jsonify({"error": "No product data provided"}), 400
        
        result = index_single_product(product_data)
        return jsonify(result), 200
    
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
    # Initialize the service
    initialize_service()
    
    # Index initial products on startup
    index_products()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)
