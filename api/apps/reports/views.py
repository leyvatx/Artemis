from core.views import BaseViewSet
from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(BaseViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        queryset = Report.objects.all()
        supervisor_id = self.request.query_params.get('supervisor')
        officer_id = self.request.query_params.get('officer')

        if supervisor_id:
            queryset = queryset.filter(supervisor_id=supervisor_id)
        if officer_id:
            queryset = queryset.filter(officer_id=officer_id)

        return queryset