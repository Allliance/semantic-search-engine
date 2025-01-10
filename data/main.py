from index import Index
from encoder import Encoder
from product import Product, ProductManager
from utils import rank_products
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Get configuration from environment variables
INDEX_NAME = os.getenv('INDEX_NAME', 'products-index')
INITIAL_INDEX = os.getenv('INITIAL_INDEX', 'false').lower() == 'true'
DIMENSION = int(os.getenv('DIMENSION', '512'))
PRODUCTS_FILE = os.getenv('PRODUCTS_FILE', 'products_1.json')
LIMIT = int(os.getenv('LIMIT', '-1'))
VERBOSE = os.getenv('VERBOSE', 'false').lower() == 'true'

# Global variables for our service
index = None
encoder = None
product_manager = None

def initialize_service():
    global index, encoder
    index = Index(INDEX_NAME, DIMENSION)
    encoder = Encoder()
    print("Service initialized successfully")

def initialize_product_manager():
    global product_manager
    product_manager = ProductManager(PRODUCTS_FILE)

def index_single_product(product):
    """Index a single product from its JSON data"""
    global index, encoder
    
    try:
        
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
    global product_manager
    
    """Index products from the initial products file"""
    print(f"Starting indexing with parameters:")
    print(f"Index name: {INDEX_NAME}")
    print(f"Dimension: {DIMENSION}")
    print(f"Products file: {PRODUCTS_FILE}")
    print(f"Limit: {LIMIT}")
    print(f"Verbose: {VERBOSE}")

    products = product_manager.get_all_products()
    
    for product in products:
        try:
            result = index_single_product(product)
            if VERBOSE:
                print(result["message"])
            
            product.recently_indexed = True
        except Exception as e:
            print(f"Error indexing product: {str(e)}")
            continue

    print("Initial product indexing completed")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/index_product', methods=['POST'])
def index_product_endpoint():
    global product_manager
    try:
        product_data = request.get_json()
        
        if not product_data:
            return jsonify({"error": "No product data provided"}), 400
        
        new_product = Product(product_data)
        
        if product_manager.product_exists(new_product.id) and product_manager.products[new_product.id].recently_indexed:
            return jsonify({"error": f"Product with id {new_product.id} already exists"}), 400
        
        result = index_single_product(product_data)
        
        if not product_manager.product_exists(new_product.id):
            product_manager.add_product(product=new_product)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_endpoint():
    global index, encoder, product_manager
    
    try:
        data = request.get_json()
        query_text = data.get('query')
        
        if not query_text:
            return jsonify({"error": "Query text is required"}), 400
        try:
            query_embedding = encoder.encode_text(query_text)
            top_image_ids = index.query(query_embedding)
            top_ids = [int(image_id.split('#')[0]) for image_id in top_image_ids]
            ranked_ids = rank_products(top_ids)
            
            response = [p.meta_data for p in product_manager.get_products_by_id(ranked_ids)]
        except Exception as e:
            print("An exception occurred while querying the index")
            print(str(e))
        
        return jsonify({"results": response}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize the service
    initialize_service()
    
    initialize_product_manager()
    
    # Index initial products on startup
    if INITIAL_INDEX:
        print("As INITIAL_INDEX is set to true, starting initial indexing")
        index_products()
    else:
        print("INITIAL_INDEX is set to false, skipping initial indexing")
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)
