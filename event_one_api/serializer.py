from events.models import OtpModel, Table

from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer


class OtpGenerationSerializer(Serializer):
    mobile = serializers.CharField()


class OtpPostSerializer(Serializer):
    otp = serializers.CharField()


class TableListSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_name']
