import pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

def create_index(index_name="products-index",
                 dimension=512):


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

if __name__ == "__main__":
    pc = create_index()
    