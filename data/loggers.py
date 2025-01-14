import logging
import os

def get_product_manager_logger():
    if os.path.exists("logs") is False:
        os.makedirs("logs")
    
    logging.basicConfig(filename="logs/product manager.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    return logging.getLogger('product manager')
