from rest_framework import viewsets
from ..models.models import Report
from ..serializers.serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
