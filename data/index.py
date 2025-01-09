from utils import init_pinecone


class ProductsIndex:
    def __init__(self,
                 index_name="products-index",
                 dimension=512,
                 ):
        self.index_name = index_name
        
        self.pc = init_pinecone(index_name, dimension)
    
    def text_query(self, text):
        query_embedding = self.encode_text(text)

        index = self.pc.Index(self.index_name)

        response = index.query(
            vector=query_embedding.tolist(),
            top_k=1,
            include_values=True,
            # include_metadata=True,
            # filter={"genre": {"$eq": "action"}}
        )
        
        return response
    
    def upsert_embeddings(self, products):
        vectors = []
        for product in products:    
            vectors += [{
                "id": f"{product.id}#{i}",
                "values": image_embedding.tolist(),
                "metadata": {},
                } for i, image_embedding in enumerate(product.image_embeddings)]

        index = self.pc.Index(self.index_name)

        index.upsert(vectors)
    
