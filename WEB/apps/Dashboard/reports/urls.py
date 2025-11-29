
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

reports = [
    # Listado de reportes por supervisor.
    path('reports/', views.ReportsListView.as_view(), name='ReportsList'),

    # Listado de reportes por oficial.
    path('reports/officer/<int:pk>/', views.ReportsByOfficerListView.as_view(), name='ReportsByOfficerList'),

    # Detalle de un reporte.
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='ReportDetail'),

    # Descarga en PDF de un reporte.
    path('reports/<int:pk>/download/', views.ReportDownloadView.as_view(), name='ReportsDownload'),

    # Crear reporte.
    path('reports/create/', views.ReportsCreateView.as_view(), name='ReportsCreate'),

    # Actualizar reporte.
    path('reports/update/<int:pk>/', views.ReportsUpdateView.as_view(), name='ReportsUpdate'),

    # Eliminar reporte.
    path('reports/delete/<int:pk>/', views.ReportsDeleteView.as_view(), name='ReportsDelete'),
]

# ---------------------------------------------------------------------------- #