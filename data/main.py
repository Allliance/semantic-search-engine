import json
from index import Index
from encoder import Encoder
from product import Product

# Configurable params
LIM = 10
INDEX_NAME = 'products-index'
DIMENSION = 512
VERBOSE = False
INDEX_PRODUCTS = True

# It can first be crawled, then saved to a file, and then loaded from the file
PRODUCTS_FILE = 'products_1.json'

def index_products():

    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products_data = json.load(f)

    products = [Product(product_data) for product_data in products_data[:LIM]]

    index = Index(INDEX_NAME, DIMENSION)
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
            if VERBOSE:
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
        
        if VERBOSE:
            print(f"Product {product.id} added to the index")
            
    print("All products have been indexed")

def query_listener():
    index = Index(INDEX_NAME, DIMENSION)
    encoder = Encoder()
    
    while True:
        query = input("Enter a query: ")
        
        if query == 'exit':
            break
        
        query_embedding = encoder.encode_text(query)
        response = index.query(query_embedding)
        
        print(response)

if __name__ == '__main__':
    if INDEX_PRODUCTS:
        index_products()
        
    query_listener()
    
