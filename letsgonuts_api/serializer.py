from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from events.models import Table, EventUsers, RegisteredUsers


class TableListSerializer(ModelSerializer):
    class Meta:
        model = Table
        exclude = ['table_order', 'event']


class FilterNameSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = EventUsers
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name


class NameDetailsSerializer(ModelSerializer):
    class Meta:
        model = EventUsers
        fields = ['mobile', 'email']


class RegisterEventSerializer(ModelSerializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    mobile = serializers.CharField()
    email = serializers.CharField()
    room_type = serializers.CharField()
    hotel_name = serializers.CharField()
    tottal_rent = serializers.CharField()

    class Meta:
        model = RegisteredUsers
        fields = ['event', 'event_user', 'table', 'first_name', 'last_name', 'mobile', 'email', 'room_type', 'hotel_name', 'tottal_rent', 'payment',
                  'amount_paid', 'event_status', ]
