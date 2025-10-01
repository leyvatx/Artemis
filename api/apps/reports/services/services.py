from ..repositories.repositories import ReportRepository


class ReportService:
    @staticmethod
    def generate_report(user, report_type, content=''):
        return ReportRepository.create_report(user, report_type, content)

    @staticmethod
    def get_user_reports(user):
        return ReportRepository.get_reports_by_user(user)

    @staticmethod
    def get_reports_by_type(report_type):
        return Report.objects.filter(report_type=report_type).order_by('-created_at')