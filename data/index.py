from utils import init_pinecone


class Index:
    def __init__(self,
                 index_name,
                 dimension=512,
                 ):
        self.index_name = index_name
        
        self.pc = init_pinecone(index_name, dimension)
    
    def get_by_id(self, ids):
        index = self.pc.Index(self.index_name)
        
        response = index.fetch(ids)
        
        return response['vectors']
    
    def query(self, query_embedding, filters=None):

        index = self.pc.Index(self.index_name)

        response = index.query(
            vector=query_embedding.tolist(),
            top_k=30,
            include_values=True,
            # include_metadata=True,
            # filter={"genre": {"$eq": "action"}}
        )['matches']
        
        
        
        return [record['id'] for record in response]
    
    def upsert_embeddings(self, elements):    
        vectors = [{
            "id": el['id'],
            "values": el['embedding'].tolist(),
            "metadata": el['metadata'],
            } for el in elements]

        index = self.pc.Index(self.index_name)

        index.upsert(vectors)
    
