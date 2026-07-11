from rest_framework import serializers


class HistoryRecordSerializer(serializers.Serializer):
    """Serializer for history record entries."""

    history_id = serializers.IntegerField()
    action = serializers.CharField()
    changes = serializers.DictField()
    timestamp = serializers.DateTimeField()
    media_entry_number = serializers.IntegerField()
