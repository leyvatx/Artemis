from rest_framework import serializers


class RelatedAttrField(serializers.CharField):
    """Convenience field for exposing a related object's attribute.

    Usage:
        owner_name = RelatedAttrField('owner.name')

    This sets `source` and `read_only=True` automatically.
    """

    def __init__(self, source_attr, **kwargs):
        kwargs.setdefault('read_only', True)
        super().__init__(source=source_attr, **kwargs)
