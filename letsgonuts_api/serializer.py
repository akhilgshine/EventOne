from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from events.models import Table, EventUsers, RegisteredUsers, STATUS_CHOICES, RoomType,MEMBER_CHOICES


class TableListSerializer(ModelSerializer):
    event_date = serializers.CharField(source='event.date')
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
        fields = ['mobile', 'email', 'first_name', 'last_name' ]


class RegisterEventSerializer(ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    mobile = serializers.CharField()
    email = serializers.CharField()
    room_type = serializers.IntegerField()
    event_status = serializers.ChoiceField(choices=STATUS_CHOICES)
    registration_type = serializers.ChoiceField(choices=MEMBER_CHOICES)
    hotel_name = serializers.CharField()
    tottal_rent = serializers.CharField(required=False)



    class Meta:
        model = RegisteredUsers
        fields = ['first_name','last_name','mobile','email','room_type','event_status','registration_type','hotel_name','tottal_rent','event', 'event_user', 'table','payment',
                  'amount_paid', 'event_status', 'registration_type']



    def validate(self, data):
        error_flag = True
        errors = []
        if not data['tottal_rent'].isdigit():
            errors.append({'tottal rent' : "Rent must be a number"})
            error_flag = False
        if data['hotel_name'] is None:
            errors.append({'hotel_name': "Hotel Name should not be blank"})
            error_flag = False
        if not error_flag:
            raise serializers.ValidationError(errors)
        return data

class RegisteredUsersSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    tableName = serializers.SerializerMethodField()
    registration_type = serializers.SerializerMethodField()

    class Meta:
        model = RegisteredUsers
        # fields = '__all__'
        fields = ['id', 'name', 'tableName', 'phone_number', 'qrcode', 'email', 'amount_paid', 'registration_type']

    def get_name(self, obj):
        return obj.event_user.first_name + '' + obj.event_user.last_name

    def get_phone_number(self, obj):
        return obj.event_user.mobile

    def get_email(self, obj):
        return obj.event_user.email

    def get_tableName(self, obj):
        return obj.table.table_name

    def get_registration_type(self, obj):
        return obj.event_status

class RoomTypeSerializer(ModelSerializer):
    hotel_name = serializers.SerializerMethodField()

    class Meta:
        model = RoomType
        fields = ['id','room_type','rooms_available','net_rate','hotel_name']


    def get_hotel_name(self, obj):
        return "Hotel Raviz Kollam"

