
# -- VIEWS ------------------------------------------------------------------- #

import requests
from datetime import datetime
from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect

from apps.Dashboard.mixins import LoginRequiredMixin
from apps.Dashboard.endpoints import REPORTS_ENDPOINTS
from apps.Dashboard.officers.views import fetch_officers

# ---------------------------------------------------------------------------- #

# Obtiene todos los reportes generados por un supervisor.
def fetch_reports_by_supervisor(request, supervisor_id):
    try:
        API_URL = REPORTS_ENDPOINTS['LIST'].format(id=supervisor_id)
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()
            reports = data.get('data', [])

            # Conversión a Datetime.
            for r in reports:
                created_at = r.get('created_at')
                if created_at:
                    try:
                        r['created_at'] = datetime.fromisoformat(created_at.replace("Z", ""))
                    except ValueError:
                        pass
            return reports
        else:
            messages.error(request, 'Ha ocurrido un error al consultar el listado de reportes.')
            return []
    except requests.exceptions.RequestException:
        messages.error(request, 'No se ha podido conectar con el servidor.')
        return []

# Obtiene todos los reportes de un oficial.
def fetch_reports_by_officer(request, officer_id):
    try:
        API_URL = REPORTS_ENDPOINTS['TARNISHED'].format(id=officer_id)
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()
            reports = data.get('data', [])

            for r in reports:
                created_at = r.get('created_at')
                if created_at:
                    try:
                        r['created_at'] = datetime.fromisoformat(created_at.replace("Z", ""))
                    except ValueError:
                        pass
            return reports
        else:
            messages.error(request, 'Ha ocurrido un error al consultar los reportes del oficial.')
            return []
    except requests.exceptions.RequestException:
        messages.error(request, 'No se ha podido conectar con el servidor.')
        return []

# Obtiene un reporte específico por su ID.
def manage_report(request, pk):
    try:
        API_URL = REPORTS_ENDPOINTS['CINDER'].format(id=pk)
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()
            report = data.get('data', {})

            # Convertir fechas a DATETIME.
            for field in ["created_at", "updated_at", "generated_at", "sent_at"]:
                if report.get(field):
                    try:
                        report[field] = datetime.fromisoformat(report[field].replace("Z", ""))
                    except ValueError:
                        pass

            return {"data": report}
        else:
            return None
    except requests.exceptions.RequestException:
        return None

# ---------------------------------------------------------------------------- #

# Listado de reportes:
class ReportsListView(LoginRequiredMixin, generic.ListView):
    template_name = 'dashboard/reports/list.html'
    paginate_by = 8
    context_object_name = 'reports'

    def get_queryset(self):
        auth_user = self.request.session.get('auth_user', {})
        supervisorId = auth_user.get('id')

        if not supervisorId:
            messages.error(self.request, 'Sesión inválida. Vuelva a iniciar sesión.')
            return []
        reports = fetch_reports_by_supervisor(self.request, supervisorId)

        query = self.request.GET.get('s', '').strip().lower()
        if query and reports:
            reports = [
                r for r in reports
                if query in r.get('title', '').lower()
                or query in r.get('report_type', '').lower()
                or query in r.get('status', '').lower()
            ]
        return reports

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('s', '')
        return context

# ---------------------------------------------------------------------------- #

# Listado de reportes (por oficial):
class ReportsByOfficerListView(LoginRequiredMixin, generic.ListView):
    template_name = 'dashboard/reports/officer.html'
    paginate_by = 4
    context_object_name = 'reports'

    def get_queryset(self):
        officer_id = self.kwargs.get('pk')
        reports = fetch_reports_by_officer(self.request, officer_id)

        query = self.request.GET.get('s', '').strip().lower()
        if query and reports:
            reports = [
                r for r in reports
                if query in r.get('title', '').lower()
                or query in r.get('report_type', '').lower()
                or query in r.get('status', '').lower()
            ]
        return reports

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('s', '')
        return context

# ---------------------------------------------------------------------------- #

# Información detallada:
class ReportDetailView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/reports/detail.html'

    def get(self, request, pk, *args, **kwargs):
        report_response = manage_report(request, pk)

        if not report_response:
            messages.error(request, 'No se pudo obtener la información del reporte.')
            return redirect('dashboard:ReportsList')

        report = report_response.get('data', report_response)

        if not report:
            messages.error(request, 'No se pudo obtener la información del reporte.')
            return redirect('dashboard:ReportsList')

        context = {
            "titleSection": f"Detalle del reporte #{report.get('report_id')}",
            "report": report
        }
        return render(request, self.template_name, context)

# Descarga en PDF del reporte:
class ReportDownloadView(LoginRequiredMixin, generic.View):
    def get(self, request, pk, *args, **kwargs):
        # TODO: ...
        messages.info(request, 'La descarga de PDF aún no está implementada.')
        return redirect('dashboard:ReportDetail', pk=pk)

# ---------------------------------------------------------------------------- #

# Creación/Registro de reportes:
class ReportsCreateView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/reports/create.html'

    def get(self, request, *args, **kwargs):
        officers = fetch_officers(request)

        context = {
            'titleSection': 'Creando reporte',
            'officers': officers
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        auth_user = request.session.get('auth_user', {})
        supervisorId = auth_user.get('id')

        if not supervisorId:
            messages.error(request, 'Sesión inválida. Vuelva a iniciar sesión.')
            return redirect('dashboard:Logout')

        reportData = {
            "supervisor": supervisorId,
            "officer": request.POST.get('officer'),
            "report_type": request.POST.get('report_type', 'Incidente'),
            "title": request.POST.get('title'),
            "content": request.POST.get('content'),
            "summary": request.POST.get('summary'),
            "status": request.POST.get('status', 'Borrador')
        }

        try:
            response = requests.post(REPORTS_ENDPOINTS['CREATE'], json=reportData)

            if response.status_code in [200, 201]:
                messages.success(request, 'El reporte ha sido registrado correctamente.')
                return redirect('dashboard:ReportsList')
            else:
                messages.error(request, 'Ha ocurrido un error al crear el reporte.')
                officers = fetch_officers(request)

                return render(request, self.template_name, {
                    'titleSection': 'Creando reporte',
                    'report_data': reportData,
                    'officers': officers
                })

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
            officers = fetch_officers(request)

            return render(request, self.template_name, {
                'titleSection': 'Creando reporte',
                'report_data': reportData,
                'officers': officers
            })

# ---------------------------------------------------------------------------- #

# Actualización de reportes:
class ReportsUpdateView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/reports/update.html'

    def get(self, request, pk, *args, **kwargs):
        report_response = manage_report(request, pk)

        if not report_response:
            return redirect('dashboard:ReportsList')

        report = report_response.get('data', report_response)
        officers = fetch_officers(request)

        context = {
            'titleSection': 'Actualizando reporte',
            'report': report,
            'officers': officers
        }

        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        updateData = {
            "title": request.POST.get('title'),
            "content": request.POST.get('content'),
            "summary": request.POST.get('summary'),
            "status": request.POST.get('status'),
            "report_type": request.POST.get('report_type'),
            "officer": request.POST.get('officer')
        }

        try:
            API_UPDATE = REPORTS_ENDPOINTS['CINDER'].format(id=pk)
            response = requests.patch(API_UPDATE, json=updateData)

            if response.status_code in [200, 201]:
                messages.success(request, 'El reporte ha sido actualizado correctamente.')
                return redirect('dashboard:ReportsList')
            else:
                messages.error(request, 'Error al actualizar el reporte.')
                officers = fetch_officers(request)
                report_response = manage_report(request, pk)
                report = report_response.get('data', report_response)

                context = {
                    'titleSection': 'Actualizando reporte',
                    'report': report,
                    'officers': officers
                }

                return render(request, self.template_name, context)

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
            return redirect('dashboard:ReportsList')

# ---------------------------------------------------------------------------- #

# Eliminación de reporte:
class ReportsDeleteView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/reports/delete.html'

    def get(self, request, pk, *args, **kwargs):
        report_response = manage_report(request, pk)

        if not report_response:
            return redirect('dashboard:ReportsList')
        
        report = report_response.get('data', report_response)

        if not report:
            return redirect('dashboard:ReportsList')
        
        context = { 'titleSection': 'Eliminando reporte', 'report': report }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        try:
            API_DELETE = REPORTS_ENDPOINTS['CINDER'].format(id=pk)
            response = requests.delete(API_DELETE)

            if response.status_code in [200, 204]:
                messages.success(request, 'El reporte ha sido eliminado correctamente.')
            else:
                messages.error(request, 'Error al eliminar el reporte.')

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
        return redirect('dashboard:ReportsList')

# ---------------------------------------------------------------------------- #