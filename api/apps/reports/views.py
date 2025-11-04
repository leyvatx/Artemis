from core.views import BaseViewSet
from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(BaseViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer