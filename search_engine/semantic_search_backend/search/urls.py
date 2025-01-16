from django.urls import path, re_path
from .views import SearchPageView, SemanticSearchAPI, KeywordSearchAPI

app_name = "search"

urlpatterns = [
    # Search page URLs - will match both with and without trailing slash
    re_path(r'^search/?$', SearchPageView.as_view(), name='search_page'),
    
    # API URLs - will match both with and without trailing slash
    re_path(r'^api/semantic-search/?$', SemanticSearchAPI.as_view(), name='semantic_search_api'),
    re_path(r'^api/keyword-search/?$', KeywordSearchAPI.as_view(), name='keyword_search_api'),

]