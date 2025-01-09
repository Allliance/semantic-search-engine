import pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt # type: ignore

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

    