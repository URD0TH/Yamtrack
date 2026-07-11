from rest_framework import serializers


class StatisticsQuerySerializer(serializers.Serializer):
    """Serializer for statistics date range parameters."""

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
