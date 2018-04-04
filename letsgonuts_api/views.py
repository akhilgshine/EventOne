# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import dateparser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date, timedelta, datetime

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED

from events.models import Table, EventUsers, RegisteredUsers, Hotels, RoomType, Event
from .serializer import TableListSerializer, FilterNameSerializer, NameDetailsSerializer, RegisterEventSerializer, \
    RegisteredUsersSerializer, RoomTypeSerializer


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_user = request.POST.get('event_user')
        try:
            event_user = EventUsers.objects.get(id=event_user)
        except EventUsers.DoesNotExist:
            event_user = None
        if serializer.validated_data:
            event_user.first_name = serializer.validated_data.pop('first_name')
            event_user.last_name = serializer.validated_data.pop('last_name')
            event_user.mobile = serializer.validated_data.pop('mobile')
            event_user.email = serializer.validated_data.pop('email')
            event_user.member_type = serializer.validated_data.pop('registration_type')
            room_type = serializer.validated_data.pop('room_type')
            hotel_name = serializer.validated_data.pop('hotel_name')
            tottal_rent = serializer.validated_data.pop('tottal_rent')
            event_user.save()
            if RegisteredUsers.objects.filter(event_user=event_user).exists():
                registered_user = RegisteredUsers.objects.get(event_user=event_user)
                previous_amount_paid = RegisteredUsers.objects.get(event_user=event_user).amount_paid
                for (key, value) in serializer.validated_data.items():
                    setattr(registered_user, key, value)
                    registered_user.amount_paid += previous_amount_paid
                registered_user.save()
            else:
                registered_user = serializer.save()
                if registered_user.qrcode is not None:
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
                    except:
                        registered_user.qrcode = 'QRT8001'
                    registered_user = serializer.save()
            try:
                room_type = RoomType.objects.get(id=room_type)
                #  TODO Validate room type
            except:
                return Response({'status': False, 'error-message': 'Invalid Room type'}, status=400)
            hotel_obj, created = Hotels.objects.get_or_create(registered_users=registered_user)
            hotel_obj.hotel_name = hotel_name
            hotel_obj.tottal_rent = tottal_rent
            hotel_obj.room_type = room_type
            hotel_obj.save()

        return Response({'status': True}, status=HTTP_201_CREATED)


class RegisteredUsersViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisteredUsersSerializer


class RoomTypeListViewSet(ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer

    def get_queryset(self):
        start_date = dateparser.parse(self.request.GET.get('start_date'))
        end_date = dateparser.parse(self.request.GET.get('end_date'))
        event_date = Event.objects.get(id=1).date
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
