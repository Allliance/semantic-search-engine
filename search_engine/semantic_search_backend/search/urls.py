from django.urls import path, re_path
from .views import SearchPageView, SearchView

app_name = "search"

urlpatterns = [
    # Search page URLs - will match both with and without trailing slash
    re_path(r'^search/?$', SearchPageView.as_view(), name='search_page'),
    
    # API URLs - will match both with and without trailing slash
    re_path(r'^api/search/?$', SearchView.as_view(), name='search_api'),

]