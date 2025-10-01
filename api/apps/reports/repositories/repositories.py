from ..models.models import Report


class ReportRepository:
    @staticmethod
    def get_all_reports():
        return Report.objects.all()

    @staticmethod
    def get_report_by_id(report_id):
        try:
            return Report.objects.get(pk=report_id)
        except Report.DoesNotExist:
            return None

    @staticmethod
    def get_reports_by_user(user):
        return Report.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def create_report(user, report_type, content=''):
        return Report.objects.create(
            user=user,
            report_type=report_type,
            content=content
        )

    @staticmethod
    def update_report(report_id, **kwargs):
        report = ReportRepository.get_report_by_id(report_id)
        if report:
            for key, value in kwargs.items():
                setattr(report, key, value)
            report.save()
            return report
        return None

    @staticmethod
    def delete_report(report_id):
        report = ReportRepository.get_report_by_id(report_id)
        if report:
            report.delete()
            return True
        return False