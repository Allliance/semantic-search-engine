from django.urls import path
from .views import SearchView, SearchPageView

app_name = "search"

urlpatterns = [
    path('api/search/', SearchView.as_view(), name='search-api'),  # API endpoint
    path('search/', SearchPageView.as_view(), name='search-page'),  # HTML page
]