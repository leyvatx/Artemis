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
    path('', api_root),
    
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('auth/', include('apps.users.auth_urls')),
    
    path('roles/', include('apps.users.role_urls')),
    path('users/', include('apps.users.urls')),
    path('supervisors/', include('apps.users.supervisor_urls')),
    path('biometrics/', include('apps.biometrics.urls')),
    path('geolocation/', include('apps.geolocation.urls')),
    path('alert-types/', include('apps.alerts.type_urls')),
    path('alerts/', include('apps.alerts.urls')),
    path('events/', include('apps.events.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
