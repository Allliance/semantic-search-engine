import pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt # type: ignore
from collections import defaultdict
import requests # type: ignore
from io import BytesIO
from PIL import Image

def rank_products(product_ids):
    all_ids = set(product_ids)
    rank_sum = defaultdict(list)
    
    for i, pid in enumerate(product_ids):
        rank_sum[pid].append(i)
        
    return sorted(all_ids, key=lambda x: sum(rank_sum[x]) / len(rank_sum[x]))

def show_image(image):
    image = image.squeeze(0)
    image = image.permute(1, 2, 0)
    plt.imshow(image)
    plt.axis('off')
    plt.show()


def init_pinecone(index_name, dimension):

    load_dotenv()

    pc = Pinecone(
            api_key=os.environ.get("PINECONE_API_KEY")
        )

    if index_name not in pc.list_indexes().names():
        pc.create_index(index_name,
                        dimension=dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1',
                        ))
        
    return pc

    
def fetch_image(image_url, verbose=False):
    response = requests.get(image_url)
        
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    elif verbose:
        print(f"Failed to fetch image from {image_url}")