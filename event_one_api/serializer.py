from events.models import OtpModel, Table, RegisteredUsers, STATUS_CHOICES, MEMBER_CHOICES

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


class RegisterSerializer(ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    mobile = serializers.CharField()
    email = serializers.CharField()
    room_type = serializers.IntegerField(required=False)
    event_status = serializers.ChoiceField(choices=STATUS_CHOICES)
    registration_type = serializers.ChoiceField(choices=MEMBER_CHOICES)
    hotel_id = serializers.IntegerField(required=False)
    tottal_rent = serializers.CharField(required=False)
    checkin_date = serializers.CharField(required=False)
    checkout_date = serializers.CharField(required=False)

    class Meta:
        model = RegisteredUsers
        fields = ['first_name', 'last_name', 'mobile', 'email', 'room_type', 'event_status', 'registration_type',
                  'hotel_id', 'tottal_rent', 'event', 'table', 'payment',
                  'amount_paid', 'reciept_file', 'checkin_date',
                  'checkout_date', 'reciept_file']

    def validate(self, data):
        error_flag = True
        errors = []
        if data.get('tottal_rent') and not data.get('tottal_rent').isdigit():
            errors.append({'tottal rent': "Rent must be a number"})
            error_flag = False
        if data.get('amount_paid') < 0:
            errors.append({'amount_paid': "Amount Paid should not be blank"})
            error_flag = False
        if not error_flag:
            raise serializers.ValidationError(errors)
        return data
