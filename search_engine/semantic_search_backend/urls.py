"""
URL configuration for semantic_search_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('search.urls')),  # Your API endpoints
    path('', RedirectView.as_view(url='/search/', permanent=True)),
    
    # Catch all unmatched URLs and redirect to /search
    re_path(r'^.*$', RedirectView.as_view(url='/search/', permanent=False)),
]