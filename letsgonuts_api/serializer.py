from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

import letsgonuts_api
from events.models import Table, EventUsers, RegisteredUsers, STATUS_CHOICES, RoomType, MEMBER_CHOICES, Hotel, \
    ImageRoomType, BookedHotel


class TableListSerializer(ModelSerializer):
    event_date = serializers.CharField(source='event.date')

    class Meta:
        model = Table
        fields = ['id', 'event_date', 'table_name', 'is_partial_payment']


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
        fields = ['id', 'mobile', 'email', 'name', 'first_name', 'last_name', 'token']


class RegisterEventSerializer(ModelSerializer):
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
                  'amount_paid', 'event_status', 'registration_type', 'reciept_number', 'reciept_file', 'checkin_date',
                  'checkout_date']

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


class ImageRoomTypeSerializer(ModelSerializer):
    class Meta:
        model = ImageRoomType
        fields = ['image']


class UserLoginSerializer(Serializer):
    # email = serializers.EmailField()
    mobile = serializers.CharField()


class OtpPostSerializer(Serializer):
    otp = serializers.CharField()


class HotelNameSerializer(ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name']


class RoomTypeSerializer(ModelSerializer):
    hotel = HotelNameSerializer()
    room_type_image = ImageRoomTypeSerializer(source='get_room_type_image', many=True)

    class Meta:
        model = RoomType
        fields = ['id', 'room_type', 'rooms_available', 'net_rate', 'hotel', 'room_type_image', 'description']


class BookedHotelSerializer(ModelSerializer):
    hotel_details = HotelNameSerializer(source='hotel', read_only=True)
    room_details = RoomTypeSerializer(source='room_type', read_only=True)

    class Meta:
        model = BookedHotel
        fields = ['checkin_date', 'checkout_date', 'hotel_details', 'room_details', 'tottal_rent']


class RegisteredUsersSerializer(ModelSerializer):
    user_details = NameDetailsSerializer(source='event_user', read_only=True)
    tableName = serializers.SerializerMethodField()
    registration_type = serializers.SerializerMethodField()
    table_details = TableListSerializer(source='table', read_only=True)
    booked_hotel = BookedHotelSerializer(source='hotel', many=True)
    payment_details = serializers.SerializerMethodField()

    class Meta:
        model = RegisteredUsers
        # fields = '__all__'
        fields = ['id', 'tableName', 'qrcode', 'amount_paid',
                  'registration_type', 'user_details', 'table_details', 'booked_hotel', 'payment_details', ]

    def get_tableName(self, obj):
        return obj.table.table_name

    def get_registration_type(self, obj):
        return obj.event_user.member_type

    def get_payment_details(self, obj):
        data = {}
        data['contributed_amount'] = obj.contributed_amount
        data['total_paid'] = obj.total_paid
        data['event_status'] = obj.event_status
        data['hotel_rent'] = obj.hotel_rent
        return data
