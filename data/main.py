import json
from index import Index
from encoder import Encoder
from product import Product
import argparse

args = {}

# It can first be crawled, then saved to a file, and then loaded from the file
PRODUCTS_FILE = 'products_1.json'

def index_products():

    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    if args.lim > 0:
        products_data = products_data[:args.lim]

    products = [Product(product_data) for product_data in products_data]

    index = Index(args.index_name, args.dimension)
    print("Successfully loaded the index")

    encoder = Encoder()
    print("Successfully loaded the encoder")

    # Now we are going to store them
    for product in products:
        # first we check if the image already exists in the index
        # if it does, we skip it
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
            if args.verbose:
                print(f"Product {product.id} already exists in the index")
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
        
        if args.verbose:
            print(f"Product {product.id} added to the index")
            
    print("All products have been indexed")

def query_listener():
    index = Index(args.index_name, args.dimension)
    encoder = Encoder()
    
    while True:
        query = input("Enter a query: ")
        
        if query == 'exit':
            break
        
        query_embedding = encoder.encode_text(query)
        response = index.query(query_embedding)
        
        print(response)

def main():
    parser = argparse.ArgumentParser(description="Run the product indexing and query listener.")

    parser.add_argument('--lim', type=int, default=10, help="Set the limit (default: 10)")
    parser.add_argument('--index_name', type=str, default='products-index', help="Set the index name (default: 'products-index')")
    parser.add_argument('--dimension', type=int, default=512, help="Set the dimension (default: 512)")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose mode (default: False)")
    parser.add_argument('--index_products', action='store_true', default=False, help="Enable products indexing (default: False)")
    parser.add_argument('--products_file', type=str, default='products_1.json', help="File path to the json of the products")

    args = parser.parse_args()

    if args.verbose:
        if args.lim != -1:
            print(f"limit products to first: {args.lim}")
        print(f"index name: {args.index_name}")
        print(f"dimension: {args.dimension}")
        print(f"index products: {args.index_products}")
    
    if args.index_products:
        index_products()
    
    query_listener()

if __name__ == '__main__':
    main()

