# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import requests
from datetime import datetime

from django.contrib.sites.models import Site
from django.utils.crypto import get_random_string
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet

from events.models import OtpModel, EventUsers,Table, RoomType, Hotel, BookedHotel, RegisteredUsers
from .serializer import OtpGenerationSerializer, OtpPostSerializer, TableListSerializer, RegisterSerializer


# Create your views here.

class OtpGenerationViewSet(ModelViewSet):
    queryset = OtpModel.objects.all()
    serializer_class = OtpGenerationSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        try:
            event_user = EventUsers.objects.get(mobile=mobile)
            if event_user.is_admin:
                otp_number = get_random_string(length=6, allowed_chars='1234567890')
                OtpModel.objects.create(otp=otp_number, mobile=mobile)
                message = "OTP for  login is %s" % (otp_number,)
                requests.get(
                    "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile + "&text=" + message +
                    "&flash=0&type=1&sender=QrtReg",
                    headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                return Response({'status': True}, status=HTTP_201_CREATED)
            else:
                return Response({'status': False, 'error': 'You are not an authenticated user'},
                                status=HTTP_201_CREATED)
        except EventUsers.DoesNotExist:
            return Response({'status': False}, status=HTTP_201_CREATED)


class OtpPostViewSet(ModelViewSet):
    queryset = OtpModel.objects.all()
    serializer_class = OtpPostSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get('otp')
        try:
            otp_obj = OtpModel.objects.get(otp=otp)
            if (datetime.now() - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'error': 'Otp Expired'}, status=400)
            if otp_obj.is_expired:
                return Response({'error': 'Otp Already Used'}, status=400)
        except OtpModel.DoesNotExist:
            return Response({'error': 'Invalid Otp'}, status=400)
        else:
            otp_obj.is_expired = True
            otp_obj.save()
            return Response({'status': True})


class TableAndMemberTypeViewSet(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [AllowAny, ]

    def list(self, request, *args, **kwargs):
        data = {}
        tables_datas = Table.objects.all()
        data['tables'] = TableListSerializer(tables_datas, many=True).data
        data['member_type'] = [{"id": 1, "type": "Tabler"}, {"id": 2, "type": "Square_Leg"}]

        return Response(data)


class RegistrationAmountType(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [AllowAny, ]

    def list(self, request, *args, **kwargs):
        member_type = request.GET.get('member_type')
        if member_type == '1':
            return Response([{'registration_type': 'Couple', 'id': 1, 'amount': 6000},
                             {'registration_type': 'Stag', 'id': 1, 'amount': 5000}])
        else:
            return Response([{'registration_type': 'Couple', 'id': 1, 'amount': 5000},
                             {'registration_type': 'Stag', 'id': 1, 'amount': 4000},
                             {'registration_type': 'Stag_Informal', 'id': 1, 'amount': 2500},
                             {'registration_type': 'Couple_Informal', 'id': 1, 'amount': 3500}])


class GetHotelList(ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [AllowAny, ]

    def list(self, request, *args, **kwargs):
        return Response([
            {
                'id': 4,
                'name': 'Raviz',
                'event_date': '12-08-2018',
                'Room': [
                    {
                        'id': 14,
                        'Name': 'Superior Room',
                        'Available': 50,
                        'date_from': '12-08-2018',
                        'date_to': '13-08-2018',
                        'rate': 2500
                    },
                    {
                        'id': 15,
                        'Name': 'Superior king',
                        'Available': 50,
                        'date_from': '12-08-2018',
                        'date_to': '13-08-2018',
                        'rate': 3500
                    }
                ]
            },
            {
                'id': 5,
                'name': 'Beach',
                'event_date': '12-08-2018',
                'Room': [
                    {
                        'id': 16,
                        'Name': 'Premium',
                        'Available': 50,
                        'date_from': '12-08-2018',
                        'date_to': '13-08-2018',
                        'rate': 2500
                    },

                ]
            },
        ])


class RegisterViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_user, created = EventUsers.objects.get_or_create(email=serializer.validated_data.get('email'),
                                                               mobile=serializer.validated_data.get('mobile'))
        if created:
            table = serializer.validated_data.get('table')
            event_user.table = table
            event_user.save()
        if serializer.validated_data:
            event_user.first_name = serializer.validated_data.pop('first_name')
            event_user.last_name = serializer.validated_data.pop('last_name')
            event_user.mobile = serializer.validated_data.pop('mobile')
            event_user.email = serializer.validated_data.pop('email')
            event_user.member_type = serializer.validated_data.pop('registration_type')
            room_type = serializer.validated_data.pop('room_type', None)
            hotel_id = serializer.validated_data.pop('hotel_id', None)
            tottal_rent = serializer.validated_data.pop('tottal_rent', None)
            checkin_date = serializer.validated_data.pop('checkin_date', None)
            checkout_date = serializer.validated_data.pop('checkout_date', None)

            event_user.save()
            if RegisteredUsers.objects.filter(event_user=event_user).exists():
                registered_user = RegisteredUsers.objects.get(event_user=event_user)
                previous_amount_paid = RegisteredUsers.objects.get(event_user=event_user).amount_paid
                for (key, value) in serializer.validated_data.items():
                    setattr(registered_user, key, value)
                registered_user.amount_paid += previous_amount_paid
                registered_user.save()
            else:
                serializer.validated_data['event_user'] = event_user
                registered_user = serializer.save()
                if not registered_user.qrcode:
                    try:
                        registered_user.qrcode = RegisteredUsers.objects.latest('qrcode').qrcode
                        if not registered_user.qrcode:
                            registered_user.qrcode = '1000'
                        else:
                            current_qrcode = registered_user.qrcode
                            new_qr_code = int(current_qrcode) + 1
                            registered_user.qrcode = new_qr_code

                    except:
                        registered_user.qrcode = '1000'
                    registered_user.is_payment_completed = True
                    registered_user = serializer.save()
            try:
                hotel = Hotel.objects.get(id=hotel_id)
            except Hotel.DoesNotExist:
                hotel = None

            if hotel and room_type:
                try:
                    room_type = RoomType.objects.get(id=room_type)
                    #  TODO Validate room type
                except RoomType.DoesNotExist:
                    return Response({'status': False, 'error-message': 'Invalid Room type'}, status=400)
                try:
                    hotel_obj = BookedHotel.objects.get(registered_users=registered_user)
                    hotel_obj.hotel = hotel
                    previous_rent = hotel_obj.tottal_rent
                except BookedHotel.DoesNotExist:
                    hotel_obj = BookedHotel.objects.create(registered_users=registered_user, hotel=hotel)
                    previous_rent = 0
                hotel_obj.room_type = room_type
                hotel_obj.tottal_rent = int(previous_rent) + int(tottal_rent)
                hotel_obj.checkin_date = checkin_date
                hotel_obj.checkout_date = checkout_date
                hotel_obj.room_type.rooms_available -= 1
                hotel_obj.room_type.save()
                hotel_obj.save()
                data = {}
                current_site = Site.objects.get_current()
                domain = current_site.domain
                data['coupon'] = '%s/api/%s/%s' % (domain, 'coupon-success', registered_user.id)
                data['status'] = True
                data['user_id'] = event_user.id
                data['registered_user_id'] = registered_user.id
                data['paid_amount'] = registered_user.total_paid
                data['due_amount'] = registered_user.total_due
                data['date'] = registered_user.created_date
                data['success_message'] = 'Successfully created'

        return Response(data)
