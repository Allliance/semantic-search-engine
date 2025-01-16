from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from models import init_db, get_db
from database import init_database
from product import Product
from product_manager import ProductManager
from index import Index
from encoder import Encoder
from utils import rank_products

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = os.getenv('INDEX_NAME', 'products-index')
INITIAL_INDEX = os.getenv('INITIAL_INDEX', 'false').lower() == 'true'
DIMENSION = int(os.getenv('DIMENSION', '512'))
PRODUCTS_FILE = os.getenv('PRODUCTS_FILE', 'products_1.json')
LIMIT = int(os.getenv('LIMIT', '-1'))
VERBOSE = os.getenv('VERBOSE', 'false').lower() == 'true'
TARGET_ENUMS = [("categories", "category_name"),
                ("currencies", "currency"),
                ("shops", "shop_name"),
                ("regions", "region"),
                ]

# Initialize FastAPI app
app = FastAPI(title="Product Search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
index: Optional[Index] = None
encoder: Optional[Encoder] = None

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    filters: Dict = {}

class ProductData(BaseModel):
    id: str
    images: List[str]
    class Config:
        extra = "allow"
        

def initialize_product_manager():
    global product_manager
    db = next(get_db())
    product_manager = ProductManager(db, PRODUCTS_FILE)

def initialize_database():
        
    init_database()
    init_db()
    print("Database initialized")
    

def initialize_service():
    global index, encoder
    
    index = Index(INDEX_NAME, DIMENSION)
    print("Index initialized")
    
    encoder = Encoder()
    print("Encoder initialized")
    

def index_single_product(product: Product) -> Dict:
    """Index a single product from its JSON data"""
    global index, encoder
    
    try:
        image_ids = [f"{product.id}#{image_url}" for image_url in product.image_urls]
        existing_ids = index.get_by_id(image_ids)
        
        to_be_added_images = []
        to_be_added_image_ids = []
        
        for i, image_url in enumerate(product.image_urls):
            if image_ids[i] in existing_ids:
                continue
            image = product.fetch_image(image_url)
            to_be_added_images.append(image)
            to_be_added_image_ids.append(image_ids[i])
        
        if len(to_be_added_images) == 0:
            if VERBOSE:
                print(f"Product {product.id} already exists in the index")
            return {"message": f"Product {product.id} already exists in the index"}

        embeddings = encoder.encode_image(to_be_added_images)
        embeddings_dict = [
            {
                'id': image_id,
                'embedding': embedding,
                'metadata': product.meta_data
            }
            for image_id, embedding in zip(to_be_added_image_ids, embeddings)
        ]
            
        index.upsert_embeddings(embeddings_dict)
        
        if VERBOSE:
            print(f"Product {product.id} added to the index")
        
        return {"message": f"Product {product.id} successfully indexed"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing product: {str(e)}")

@app.on_event("startup")
async def startup_event():
    initialize_database()
    initialize_service()
    initialize_product_manager()

@app.get("/health")
async def health_check():
    return {"message": "healthy"}

@app.post("/index_product")
async def index_product_endpoint(
    product_data: ProductData,
    db: Session = Depends(get_db)
):
    product_manager = ProductManager(db)
    
    try:
        new_product = Product(**product_data.dict())
        
        if product_manager.product_exists(new_product.id):
            raise HTTPException(
                status_code=400,
                detail=f"Product with id {new_product.id} already exists"
            )
        
        result = index_single_product(new_product)
        product_manager.add_product(product=new_product)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enums")
async def get_enums(db: Session = Depends(get_db)):
    product_manager = ProductManager(db)
    
    return {
        e[0]: product_manager.get_enum_values(e[1]) for e in TARGET_ENUMS
    }

@app.post("/query")
async def query_endpoint(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    product_manager = ProductManager(db)
    
    try:
        query_embedding = encoder.encode_text(query_request.query)
        top_image_ids = index.query(query_embedding, query_request.filters)
        top_ids = [image_id.split('#')[0] for image_id in top_image_ids]
        ranked_ids = rank_products(top_ids)
        
        products = product_manager.get_products_by_id(ranked_ids)
        response = [product.to_dict() for product in products]
        
        return {"results": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)