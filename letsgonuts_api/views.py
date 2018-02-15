# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from events.models import Table, EventUsers, RegisteredUsers, Hotels, RoomType
from .serializer import TableListSerializer, FilterNameSerializer, NameDetailsSerializer, RegisterEventSerializer

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
        table_id = self.kwargs.get('table_id')
        input_char = self.kwargs.get('input_char')
        filter_names = EventUsers.objects.filter(table__id=table_id, first_name__icontains=input_char)
        return filter_names


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
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RegisterEventViewSet(ModelViewSet):
    queryset = RegisteredUsers.objects.all()
    serializer_class = RegisterEventSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # table_id = self.kwargs.get('table_id')
        event_user = request.POST.get('event_user')
        try:
            event_user = EventUsers.objects.get(id=event_user)
        except EventUsers.DoesNotExist:
            event_user = None
        if serializer.validated_data:
            event_user.first_name = serializer.validated_data.get('first_name')
            event_user.last_name = serializer.validated_data.get('last_name')
            event_user.mobile = serializer.validated_data.get('mobile')
            event_user.email = serializer.validated_data.get('email')
            serializer.validated_data.pop('first_name')
            serializer.validated_data.pop('last_name')
            serializer.validated_data.pop('email')
            serializer.validated_data.pop('mobile')
            room_type = serializer.validated_data.pop('room_type')
            hotel_name = serializer.validated_data.pop('hotel_name')
            tottal_rent = serializer.validated_data.pop('tottal_rent')
            event_user.save()
            obj = serializer.save()
            room_type = RoomType.objects.get(id=room_type)
            #  TODO Validate room type
            Hotels.objects.create(registered_users=obj,
                                  hotel_name=hotel_name,
                                  tottal_rent=tottal_rent,
                                  room_type=room_type)
        return Response({'status': True}, status=HTTP_201_CREATED)





