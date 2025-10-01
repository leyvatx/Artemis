from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_positive(value):
    if value <= 0:
        raise ValidationError(_('Value must be positive.'))


def validate_email_domain(value):
    if not value.endswith('@example.com'):
        raise ValidationError(_('Email must be from example.com domain.'))