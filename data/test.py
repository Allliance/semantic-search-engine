import pinecone
from .main import create_index
import clip
import torch
from PIL import Image
from torchvision import transforms
import torch
import os
import numpy as np
import matplotlib.pyplot as plt # type: ignore

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device)

index_name = "test-index"

pc = create_index(index_name)
# Load test images and their embeddings


def load_image(image_path):
    return preprocess(Image.open("path_to_your_image.jpg")).unsqueeze(0).to(device)
    

# show the image using plt
def show_image(image):
    image = image.squeeze(0)
    image = image.permute(1, 2, 0)
    plt.imshow(image)
    plt.axis('off')
    plt.show()

def upsert_embeddings(product_ids, embeddings):
    # Convert embeddings to a list of tuples (id, vector)
    vectors = [(str(product_id), embedding.tolist()) for product_id, embedding in zip(product_ids, embeddings)]

    # Connect to the index
    index = pinecone.Index(index_name)

    # Upsert the embeddings
    index.upsert(vectors)    

image_files = {
    'cat': 'test_images/cat.png',
    'dog': 'test_images/dog.png',
    'elephant': 'test_images/elephant.jpg',
}

name = 'dog'

image = load_image(image_files[name])
show_image(image)


# Get the image embedding
image_embedding = model.encode_image(image)
image_embedding = image_embedding.cpu().detach().numpy()

# Upsert the image embedding
upsert_embeddings([name], [image_embedding])