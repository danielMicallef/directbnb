"""
URL configuration for directbnb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from apps.users import api_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("apps.users.api_urls")),
    # OpenAPI schema and documentation (protected in production)
    path("api/schema/", api_views.ProtectedSpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", api_views.ProtectedSpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", api_views.ProtectedSpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Web views
    path("", include("apps.users.urls")),
]
