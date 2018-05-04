from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from events.models import Table, EventUsers, RegisteredUsers, STATUS_CHOICES, RoomType, MEMBER_CHOICES, Hotel,ImageRoomType


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

    token = serializers.CharField(source='auth_token.key')
    name = serializers.CharField(source='get_full_name')

    class Meta:
        model = EventUsers
        fields = ['mobile', 'email', 'name', 'first_name', 'last_name', 'token']


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
        fields = ['first_name', 'last_name', 'mobile', 'email', 'room_type', 'event_status', 'registration_type',
                  'hotel_name', 'tottal_rent', 'event', 'event_user', 'table', 'payment',
                  'amount_paid', 'event_status', 'registration_type']

    def validate(self, data):
        error_flag = True
        errors = []
        if not data['tottal_rent'].isdigit():
            errors.append({'tottal rent': "Rent must be a number"})
            error_flag = False
        if data['hotel_name'] is None:
            errors.append({'hotel_name': "Hotel Name should not be blank"})
            error_flag = False
        if data['amount_paid'] is None:
            errors.append({'amount_paid': "Amount Paid should not be blank"})
            error_flag = False
        if not error_flag:
            raise serializers.ValidationError(errors)
        return data


class RegisteredUsersSerializer(ModelSerializer):

    user_details = NameDetailsSerializer(source='event_user', read_only=True)
    tableName = serializers.SerializerMethodField()
    registration_type = serializers.SerializerMethodField()

    class Meta:
        model = RegisteredUsers
        # fields = '__all__'
        fields = ['id', 'tableName', 'qrcode','amount_paid',
                  'registration_type', 'user_details']


    def get_tableName(self, obj):
        return obj.table.table_name

    def get_registration_type(self, obj):
        return obj.event_status


class ImageRoomTypeSerializer(ModelSerializer):
    class Meta:
        model = ImageRoomType
        fields = ['image']


class RoomTypeSerializer(ModelSerializer):
    hotel_name = serializers.SerializerMethodField()
    room_type_image = ImageRoomTypeSerializer(source='get_room_type_image', many=True)

    class Meta:
        model = RoomType
        fields = ['id', 'room_type', 'rooms_available', 'net_rate', 'hotel_name','room_type_image']

    def get_hotel_name(self,obj):
        return Hotel.objects.all()[0].name


class UserLoginSerializer(Serializer):

    email = serializers.EmailField()
    mobile = serializers.CharField()


class OtpPostSerializer(Serializer):

    otp = serializers.CharField()


class HotelNameSerializer(ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name']


