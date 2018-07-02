# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

import dateparser
import os

from PIL import Image
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import Q
from datetime import date, timedelta, datetime

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
import imgkit
from rest_framework.renderers import TemplateHTMLRenderer
from django.conf import settings

from events.utils import encoded_id
from events_app.settings import DEFAULT_FROM_EMAIL

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED
import requests
from events.models import Table, EventUsers, RegisteredUsers, BookedHotel, RoomType, Event, OtpModel, Hotel, \
    EventDocument
from .serializer import TableListSerializer, FilterNameSerializer, NameDetailsSerializer, RegisterEventSerializer, \
    RegisteredUsersSerializer, RoomTypeSerializer, UserLoginSerializer, OtpPostSerializer, HotelNameSerializer, \
    EventDocumentSerializer


# Create your views here.


class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = {}
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                response['status'] = 'success'
                response['message'] = 'User logged in succesfully'
                token, _ = Token.objects.get_or_create(user=user)
                response['token'] = token.key
                return Response(response, status=200)
            else:
                response['status'] = 'failed'
                response['message'] = 'User not activated'
                return Response(response, status=HTTP_401_UNAUTHORIZED)
        response['status'] = 'failed'
        response['message'] = 'Login failed'
        return Response(response, status=HTTP_401_UNAUTHORIZED)


class TableListViewSet(ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableListSerializer
    permission_classes = [AllowAny, ]


class FilterNameViewSet(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = FilterNameSerializer

    def get_queryset(self):
        table_id = self.kwargs.get('table_id', '')
        input_char = self.kwargs.get('input_char', '')
        filter_names = EventUsers.objects.filter(table__id=table_id, first_name__icontains=input_char)
        return filter_names

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response('No data found', status=HTTP_400_BAD_REQUEST)
        return super(FilterNameViewSet, self).list(request, *args, **kwargs)


class NameDetailsViewSet(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = NameDetailsSerializer

    def list(self, request, *args, **kwargs):
        table_id = request.GET.get('table_id')
        name_id = request.GET.get('name_id')
        try:
            name_details = EventUsers.objects.get(table__id=table_id, id=name_id)
        except EventUsers.DoesNotExist:
            name_details = None
        instance = name_details
        if not instance:
            return Response('No data found', status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RegisterEventViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisterEventSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_user, created = EventUsers.objects.get_or_create(email=serializer.validated_data.get('email'),
                                                               mobile=serializer.validated_data.get('mobile'))
        if created:
            try:
                table = Table.objects.get(id=serializer.validated_data.get('hotel_id'))
                event_user.table = table
                event_user.save()
            except Table.DoesNotExist:
                return Response({'status': False, 'error-message': 'Invalid Table'}, status=400)

        token, _ = Token.objects.get_or_create(user=event_user)
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
                        if not registered_user.qrcode.split('QRT')[1].startswith('8'):
                            registered_user.qrcode = 'QRT8001'
                        else:
                            qrcode_updated = registered_user.qrcode[-3:]
                            qrcode_updated_increment = int(qrcode_updated) + 1
                            qrcode_updated_length = len(str(qrcode_updated_increment))
                            if qrcode_updated_length == 1:
                                registered_user.qrcode = str('QRT8') + '00' + str(qrcode_updated_increment)
                            if qrcode_updated_length == 2:
                                registered_user.qrcode = str('QRT8') + '0' + str(qrcode_updated_increment)
                            else:
                                registered_user.qrcode = str('QRT8') + str(qrcode_updated_increment)
                    except:
                        registered_user.qrcode = 'QRT8001'
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

        return Response({'status': True, 'user_id': event_user.id, 'registered_user_id': registered_user.id},
                        status=HTTP_201_CREATED)


class RegisteredUsersViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisteredUsersSerializer


class RoomTypeListViewSet(ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        start_date = dateparser.parse(self.request.GET.get('start_date'))
        end_date = dateparser.parse(self.request.GET.get('end_date'))
        hotel_id = self.request.GET.get('hotel_id')
        event_id = self.request.GET.get('event_id')
        try:
            hotel = Hotel.objects.get(id=hotel_id)
            self.queryset = hotel.get_hotel_room_types.all()
        except Hotel.DoesNotExist:
            return []
        try:
            event_date = Event.objects.get(id=event_id).date
        except Event.DoesNotExist:
            return []
        day_before_event = event_date - timedelta(1)
        day_before_event_with_time = datetime.combine(day_before_event, datetime.min.time())
        day_after_event = event_date + timedelta(1)
        day_before_after_with_time = datetime.combine(day_after_event, datetime.min.time())
        if start_date < day_before_event_with_time or end_date > day_before_after_with_time:
            return []
        return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response('No rooms found', status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserLoginViewSet(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data.get('mobile')
        otp_number = get_random_string(length=6, allowed_chars='1234567890')
        otp_obj = OtpModel.objects.create(otp=otp_number, mobile=mobile)
        message = "OTP for letsgonuts login is %s" % (otp_number,)
        requests.get(
            "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile + "&text=" + message +
            "&flash=0&type=1&sender=QrtReg",
            headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
        headers = self.get_success_headers(serializer.data)
        return Response('sent OTP MESSAGE  successfully', status=HTTP_201_CREATED, headers=headers)


class OtpPostViewSet(ModelViewSet):
    queryset = EventUsers.objects.all()
    serializer_class = OtpPostSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = request.POST.get('otp')
        try:
            otp_obj = OtpModel.objects.get(otp=otp)
            if (datetime.now() - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'error': 'Otp Expired'}, status=400)
        except OtpModel.DoesNotExist:
            return Response({'error': 'Invalid otp'}, status=400)
        response = {}
        try:
            event_user = EventUsers.objects.get(mobile=otp_obj.mobile)
        except EventUsers.DoesNotExist:
            event_user = None
        if not event_user:
            response['status'] = 1
            return Response(response, status=200)
        token, _ = Token.objects.get_or_create(user=event_user)
        if event_user.registered_obj:
            reg_user = event_user.registered_obj
            response = RegisteredUsersSerializer(reg_user).data
            response['status'] = 3
        else:
            response = NameDetailsSerializer(event_user).data
            response['status'] = 2
        return Response(response, status=200)


class HotelNameViewSet(ModelViewSet):
    queryset = Hotel.objects.order_by('name')
    serializer_class = HotelNameSerializer
    permission_classes = [AllowAny, ]


class PaymentDetailsViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisteredUsersSerializer
    permission_classes = [AllowAny, ]


class CouponSuccessViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisteredUsersSerializer
    permission_classes = [AllowAny, ]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        current_site = Site.objects.get_current()
        domain = current_site.domain

        options = {
            'format': 'png',
            'encoding': "UTF-8",
        }
        url = domain + str(reverse_lazy('invoice_view', kwargs={'pk': encoded_id(instance.id)}))
        imgkit.from_url(url, os.path.join(settings.BASE_DIR, 'Media', 'coupon.png'), options=options)
        try:
            image_data = open(os.path.join(settings.BASE_DIR, 'Media', 'coupon.png'), "rb").read()
            return HttpResponse(image_data, content_type="image/png")
        except IOError as e:
            response = HttpResponse(content_type="image/png")
            return response


class EventDocumentViewSet(ModelViewSet):
    queryset = EventDocument.objects.all()
    serializer_class = EventDocumentSerializer
    permission_classes = [AllowAny, ]
