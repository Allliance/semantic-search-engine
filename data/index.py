from pinecone import Pinecone, ServerlessSpec
from utils import init_pinecone


class ProductsIndexer:
    def __init__(self,
                 api_key,
                 index_name="products-index",
                 dimension=512,
                 ):
        self.index_name = index_name
        
        self.pc = init_pinecone(index_name, dimension)
            
        
    def init_index(self):
        pc = create_index(self.index_name)
        return pc
    
