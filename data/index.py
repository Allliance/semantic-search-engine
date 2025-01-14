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
        
        pinecone_filters = self._prepare_pinecone_filters(filters)

        response = index.query(
            vector=query_embedding.tolist(),
            top_k=30,
            include_values=True,
            include_metadata=True,
            filter=pinecone_filters
        )['matches']
        
        return [record['id'] for record in response]
    
    def _prepare_pinecone_filters(self, filters):
        """Convert API filters to Pinecone filter format"""
        if not filters:
            return None
            
        pinecone_filters = {"$and": []}
        
        # For each filter, we need to check both the value and ensure the field exists
        if 'category' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"category_name": {"$exists": True}},
                    {"category_name": {"$eq": filters['category']}}
                ]
            })
            
        if 'price' in filters:
            price_filter = {"$and": [
                {"current_price": {"$exists": True}},
                {"currency": {"$exists": True}},
                {"currency": {"$eq": filters['price']['currency']}}
            ]}
            
            if 'min' in filters['price']:
                price_filter["$and"].append({
                    "current_price": {"$gte": filters['price']['min']}
                })
            if 'max' in filters['price']:
                price_filter["$and"].append({
                    "current_price": {"$lte": filters['price']['max']}
                })
            
            pinecone_filters["$and"].append(price_filter)
            
        if 'update_date' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"update_date": {"$exists": True}},
                    {"update_date": {"$eq": filters['update_date']}}
                ]
            })
            
        if 'shop' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"shop_name": {"$exists": True}},
                    {"shop_name": {"$eq": filters['shop']}}
                ]
            })
            
        if 'status' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"status": {"$exists": True}},
                    {"status": {"$eq": filters['status']}}
                ]
            })
            
        if 'region' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"region": {"$exists": True}},
                    {"region": {"$eq": filters['region']}}
                ]
            })
            
        if 'discount' in filters:
            pinecone_filters["$and"].append({
                "$and": [
                    {"off_percent": {"$exists": True}},
                    {"off_percent": {"$lte": filters['discount']}}
                ]
            })
        
        return pinecone_filters if pinecone_filters["$and"] else None
    
    def upsert_embeddings(self, elements):    
        vectors = [{
            "id": el['id'],
            "values": el['embedding'].tolist(),
            "metadata": el['metadata'],
            } for el in elements]

        index = self.pc.Index(self.index_name)

        index.upsert(vectors)
    
