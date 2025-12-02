"""
URL configuration for config project.

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
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def api_root(request):
    """Minimal API root returning available top-level endpoints as JSON."""
    return JsonResponse({
        "message": "Artemis API",
        "endpoints": [
            "docs/", "schema/", "redoc/", "roles/", "users/", "biometrics/",
            "geolocation/", "alerts/", "events/", "recommendations/", "reports/",
        ],
    })

urlpatterns = [
    path('api/', api_root),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('api/auth/', include('apps.users.auth_urls')),
    
    # API Endpoints
    path('api/roles/', include('apps.users.role_urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/supervisors/', include('apps.users.supervisor_urls')),
    path('api/biometrics/', include('apps.biometrics.urls')),
    path('api/geolocation/', include('apps.geolocation.urls')),
    path('api/alert-types/', include('apps.alerts.type_urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
