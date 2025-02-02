import torch
from index import Index
from encoder import CLIPEncoder

device = "cuda" if torch.cuda.is_available() else "cpu"

index_name = "test-index"


index = Index("test-index")
print("Indexer loaded")
encoder = CLIPEncoder()
print("CLIP encoder loaded")

image_files = {
    'cat': 'test_images/cat.png',
    'dog': 'test_images/dog.png',
    'elephant': 'test_images/elephant.jpg',
}

names = image_files.keys()
image_paths = [image_files[name] for name in names]

print("Encoding images ...")
embeddings, images = encoder.load_image_and_embedding(image_paths)


print("Images encoded successfully! Now you can enter your query:")

while True:
    query = input()

    query_embedding = encoder.encode_text(query)
    
    response = index.query(query_embedding)
    
    best_match = response['matches'][0]
    print("Best match ID:", best_match['id'])
    print("Best match score:", best_match['score'])
    
    print("*"*10)