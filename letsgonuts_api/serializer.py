from django.contrib.sites.models import Site
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from events.models import (MEMBER_CHOICES, STATUS_CHOICES, BookedHotel,
                           EventDocument, EventUsers,
                           Hotel, ImageRoomType,
                           RegisteredUsers, RoomType, Table, IDDocumentsPhoto, DAY_TYPE_CHOICES, TIME_TYPE_CHOICES,
                           UserFoodCoupon)
from user_registration.validators import validate_phone


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
    id_card_type = serializers.CharField(required=False, write_only=True)
    room_type = serializers.IntegerField(required=False)
    event_status = serializers.ChoiceField(choices=STATUS_CHOICES)
    registration_type = serializers.ChoiceField(choices=MEMBER_CHOICES)
    hotel_id = serializers.IntegerField(required=False)
    tottal_rent = serializers.CharField(required=False)
    checkin_date = serializers.CharField(required=False)
    checkout_date = serializers.CharField(required=False)
    id_images = serializers.ListField(child=serializers.FileField(), required=False, write_only=True)

    class Meta:
        model = RegisteredUsers
        fields = ['first_name', 'last_name', 'mobile', 'email', 'room_type', 'event_status', 'registration_type',
                  'hotel_id', 'tottal_rent', 'event', 'table', 'payment',
                  'amount_paid', 'event_status', 'registration_type', 'reciept_number', 'reciept_file', 'checkin_date',
                  'checkout_date', 'id_images', 'id_card_type']

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
        fields = ['checkin_date', 'checkout_date', 'hotel_details', 'room_details', 'tottal_rent', 'room_number']


class IDImageFileListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = IDDocumentsPhoto
        fields = ['image_url', 'id_card_type']

    def get_image_url(self, obj):
        current_site = Site.objects.get_current()
        domain = current_site.domain
        url = '%s%s' % (domain, obj.id_card_images.url)
        return url


class RegisteredUsersSerializer(ModelSerializer):
    user_details = NameDetailsSerializer(source='event_user', read_only=True)
    tableName = serializers.SerializerMethodField()
    registration_type = serializers.SerializerMethodField()
    table_details = TableListSerializer(source='table', read_only=True)
    booked_hotel = BookedHotelSerializer(source='hotel', many=True)
    id_images = IDImageFileListSerializer(source='ids_img', many=True, read_only=True)
    payment_details = serializers.SerializerMethodField()
    coupon_url = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()

    class Meta:
        model = RegisteredUsers
        fields = ['id', 'tableName', 'qrcode', 'amount_paid',
                  'registration_type', 'user_details', 'table_details', 'booked_hotel', 'payment_details',
                  'coupon_url', 'is_approved', 'id_images']

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

    def get_coupon_url(self, obj):
        current_site = Site.objects.get_current()
        domain = current_site.domain
        url = '%s/api/%s/%s' % (domain, 'coupon-success', obj.id)
        return url

    def get_is_approved(self, obj):
        return obj.event_user.is_approved


class EventDocumentSerializer(ModelSerializer):
    class Meta:
        model = EventDocument
        fields = ['event_videos', 'description', 'event_images']


# class NfcCouponSerializer(ModelSerializer):
#     mobile = serializers.CharField(write_only=True, validators=[validate_phone], required=False)
#     email = serializers.CharField(write_only=True, required=False)
#
#     class Meta:
#         model = NfcCoupon
#         fields = ['card_number', 'mobile', 'email']
#
#     def validate_card_number(self, card_number):
#         if NfcCoupon.objects.filter(card_number=card_number).exists():
#             raise serializers.ValidationError("This card number already exist")
#         return card_number
#
#
# class FridayLunchBookingSerializer(ModelSerializer):
#     nfc_card_number = serializers.CharField(write_only=True, required=False)
#
#     class Meta:
#         model = FridayLunchBooking
#         fields = ['payment_type', 'pos_number', 'nfc_card_number']
#
#     def validate_nfc_card_number(self, card_number):
#         try:
#             nfc_coupon = NfcCoupon.objects.get(card_number=card_number)
#             if nfc_coupon.registered_user.get_friday_lunch_users.all():
#                 raise serializers.ValidationError("This user already booked friday lunch")
#             return card_number
#         except NfcCoupon.DoesNotExist:
#             raise serializers.ValidationError("Invalid Coupon")


class CouponUserScanSerializer(Serializer):
    user_encoded_id = serializers.CharField(required=True)
    day = serializers.ChoiceField(choices=DAY_TYPE_CHOICES, required=True)
    time = serializers.ChoiceField(choices=TIME_TYPE_CHOICES, required=True)


class ScannedCouponDetailsSerializer(Serializer):
    coupon_users = serializers.SerializerMethodField()
    day = serializers.ChoiceField(choices=DAY_TYPE_CHOICES, write_only=True)
    time = serializers.ChoiceField(choices=TIME_TYPE_CHOICES, write_only=True)

    class Meta:
        model = UserFoodCoupon
        fields = ['coupon_users', 'day', 'time']

    def get_coupon_users(self, obj):
        data = {}
        data['name'] = obj.coupon_user.event_user.get_full_name()
        data['qrcode'] = obj.coupon_user.qrcode
        data['qrcode'] = obj.coupon_user.event_status
        return data
