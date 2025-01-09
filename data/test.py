import torch
from index import ProductsIndex
from encoder import CLIPEncoder

device = "cuda" if torch.cuda.is_available() else "cpu"

index_name = "test-index"


index = ProductsIndex("test-index")
encoder = CLIPEncoder()

image_files = {
    'cat': 'test_images/cat.png',
    'dog': 'test_images/dog.png',
    'elephant': 'test_images/elephant.jpg',
}

names = image_files.keys()
image_paths = [image_files[name] for name in names]

embeddings, images = encoder.load_image_and_embedding(image_paths)


while True:
    query = input()

    response = index.text_query(query)
    
    best_match = response['matches'][0]
    print("Best match ID:", best_match['id'])
    print("Best match score:", best_match['score'])
    
    print("*"*10)