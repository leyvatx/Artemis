
# -- VIEWS ------------------------------------------------------------------- #

import requests
from datetime import datetime
from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect

from io import BytesIO
from pathlib import Path
from reportlab.lib import colors
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)

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
def ReportsDownload(request, report_id):
    
    # Datos a mostrar:
    response = manage_report(request, report_id)
    report = response.get('data', response)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
        leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)


    # Estilos: 
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BrandTitle', fontSize=14, leading=20,
        textColor=colors.HexColor("#242D2D"), fontName='Times-Bold'))

    styles.add(ParagraphStyle(name='BrandSubtitle', fontSize=8, leading=10,
        textColor=colors.HexColor("#445D5D"), fontName='Times-Roman'))
    
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=10, leading=14,
        alignment=2, textColor=colors.HexColor("#242D2D"), fontName='Times-Bold'))
    
    styles.add(ParagraphStyle(name='Meta', fontSize=10, leading=12,
        alignment=2, textColor=colors.HexColor("#445D5D"), fontName='Times-Roman'))
    
    styles.add(ParagraphStyle(name='Label', fontSize=10, leading=12,
        textColor=colors.HexColor("#445D5D"), fontName='Times-Roman'))
    
    styles.add(ParagraphStyle(name='Value', fontSize=10, leading=12,
        textColor=colors.HexColor("#242D2D"), fontName='Times-Roman'))
    
    styles.add(ParagraphStyle(name='Justified', fontSize=10, leading=14,
        textColor=colors.HexColor("#242D2D"), fontName='Times-Roman', alignment=4))

    artemisLogo = Path(__file__).resolve().parent.parent.parent.parent / 'statics' / 'images' / 'mainicon.webp'


    # Organización del documento: 
    elements = []
    elements.append(Spacer(1, 30))


    # Encabezado:
    mainHeader = []

    if artemisLogo.exists(): # Logotipo (con el nombre).
        mainHeader.append(Image(str(artemisLogo), width=48, height=48))
    else: # Añade un espaciado de encontrar el logotipo.
        mainHeader.append(Spacer(1, 0))

    mainHeader.append(Paragraph('ARTEMIS', styles['BrandTitle']))
    mainHeader.append(Paragraph('Generación de reportes', styles['BrandSubtitle']))

    created_at = report.get('created_at')
    createdSTR = created_at.strftime("%d/%m/%Y %H:%M") if hasattr(created_at, "strftime") else str(created_at or "")

    headerTable = Table([
        [
            Table([[mainHeader[0], Table([[mainHeader[1]], [mainHeader[2]]],
                colWidths=[200], style=TableStyle([
                    ("LEFTPADDING", (0,0), (-1,-1), 6),
                    ("TOPPADDING", (0,0), (-1,-1), 0),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ]))]], colWidths=[56, 224],
            
            style=TableStyle([
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("TOPPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ])),

            Table([
                [Paragraph(f"{str(report.get('title') or 'Reporte')}", styles['SectionTitle'])],
                [Paragraph(f"Creado el {createdSTR}", styles['Meta'])]
            ], colWidths=[220], hAlign='RIGHT',

            style=TableStyle([
               ("LEFTPADDING", (0,0), (-1,-1), 0),
               ("TOPPADDING", (0,0), (-1,-1), 0),
               ("BOTTOMPADDING", (0,0), (-1,-1), 0),
           ])),
        ]
    ], colWidths=[320, 220])

    # Borde separador. 
    headerTable.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW", (0,0), (-1,0), 0.25, colors.HexColor("#D7E0DF")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))

    elements.append(headerTable)
    elements.append(Spacer(1, 30))

    # status del reporte:
    status = str(report.get("status") or "")

    statusBG = {
        "Borrador": colors.HexColor("#D7E0DF"),
        "Archivado": colors.HexColor("#F5D58A"),
        "Generado": colors.HexColor("#A0BD9E"),
    }.get(status, colors.HexColor("#C5CACB"))

    statusText = {
        "Borrador": colors.HexColor("#97B1AF"),
        "Archivado": colors.HexColor("#EDA632"),
        "Generado": colors.HexColor("#61885F"),
    }.get(status, colors.HexColor("#445D5D"))
    
    statusTable = Table([
        [
            Paragraph('Estado', styles['Label']),
            Table([[
                Paragraph(f'<b>{status}</b>', ParagraphStyle(
                    name='StatusValue', parent=styles['Value'],
                    textColor=statusText, alignment=1
                ))
            ]], colWidths=[80], style=TableStyle([
                ("BACKGROUND", (0,0), (0,0), statusBG),
                ("BOX", (0,0), (0,0), 0.25, statusText),
                ("INNERPADDING", (0,0), (0,0), 2),
                ("VALIGN", (0,0), (0,0), "MIDDLE"),
            ]))
        ]
    ], colWidths=[78, 100], hAlign='LEFT')

    statusTable.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 50),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elements.append(statusTable)
    elements.append(Spacer(1, 18))


    # Datos del supervisor y del oficial:
    supervisor = report.get('supervisor_summary', {}) or {}
    officer = report.get('officer_summary', {}) or {}

    Catarina = [
        Paragraph('Título', styles['Label']),
        Paragraph(str(report.get("title") or ""), styles['Value']),
        Spacer(1, 8),
        Paragraph('Supervisor', styles['Label']),
        Paragraph(f"{supervisor.get('name','')} ({supervisor.get('email','')})", styles['Value']),
    ]

    Solaire = [
        Paragraph('Tipo', styles['Label']),
        Paragraph(str(report.get("report_type") or ""), styles['Value']),
        Spacer(1, 8),
        Paragraph('Oficial', styles['Label']),
        Paragraph(f"{officer.get('name','')} ({officer.get('badge_number','')})", styles['Value']),
    ]

    grid = Table([[Catarina, Solaire]], colWidths=[280, 220])
    grid.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    
    elements.append(grid)
    elements.append(Spacer(1, 18))

    # Resumen:
    summaryTable = Table([
        [Paragraph('Resumen', styles['Label'])],

        [Table([[
            Paragraph(str(report.get('summary') or 'Sin resumen'), ParagraphStyle(
                name="SummaryValue", parent=styles['Justified']))
            ]], colWidths=[None])]
        ], colWidths=[None], hAlign='LEFT')

    summaryTable.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 50),
        ("RIGHTPADDING", (0,0), (-1,-1), 50),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))

    elements.append(summaryTable)
    elements.append(Spacer(1, 18))

    # Contenido:
    contentTable = Table([
        [Paragraph('Contenido', styles['Label'])],

        [Table([[
            Paragraph(str(report.get('content') or ''), ParagraphStyle(
                name="SummaryValue", parent=styles['Justified']))
            ]], colWidths=[None])]
        ], colWidths=[None], hAlign='LEFT')

    contentTable.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 50),
        ("RIGHTPADDING", (0,0), (-1,-1), 50),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))

    elements.append(contentTable)
    elements.append(Spacer(1, 30))

    # Última actualización:
    updatedDate = report.get("updated_at")
    updatedSTR = updatedDate.strftime("%d/%m/%Y %H:%M") if hasattr(updatedDate, "strftime") else str(updatedDate or "")

    lastUpdate = Table([[
        Paragraph(f'Última actualización: {updatedSTR}', styles['Meta'])
    ]], colWidths=[600])

    lastUpdate.setStyle(TableStyle([
        ("RIGHTPADDING", (0,0), (0,0), 50),
        ("LEFTPADDING", (0,0), (0,0), 0),
        ("TOPPADDING", (0,0), (0,0), 0),
        ("BOTTOMPADDING", (0,0), (0,0), 0),
    ]))

    elements.append(lastUpdate)
    elements.append(Spacer(1, 18))


    def draw_card_bg(canvas, _doc):
        x = doc.leftMargin
        y = doc.bottomMargin
        w = doc.width
        h = doc.height
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F6F8F8"))
        canvas.setStrokeColor(colors.HexColor("#EEEEEE"))
        canvas.rect(x, y, w, h, fill=1, stroke=1)
        canvas.restoreState()

    doc.build(elements, onFirstPage=draw_card_bg, onLaterPages=draw_card_bg)
    buffer.seek(0)

    filename = f"Reporte: {report.get('title')}.pdf"

    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="{filename}"'
    })

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