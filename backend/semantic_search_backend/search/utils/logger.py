import logging

# Get the logger for the search app
logger = logging.getLogger('search')

def log_search_request(query):
    """Log search request details"""
    logger.info(f'Search request - Query: "{query}"')