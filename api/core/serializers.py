from rest_framework import serializers


class RelatedAttrField(serializers.RelatedField):
    """
    A field for accessing nested attributes on related objects.
    Usage: user_name = RelatedAttrField('user.name')
    """
    def __init__(self, attr_path, **kwargs):
        self.attr_path = attr_path
        super().__init__(**kwargs)

    def to_representation(self, value):
        attrs = self.attr_path.split('.')
        for attr in attrs:
            value = getattr(value, attr, None)
            if value is None:
                return None
        return value


class PaginatedResponseSerializer(serializers.Serializer):
    """Standard paginated response format"""
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()
