import json

with open("test_products.json") as f:
    print(json.load(f))