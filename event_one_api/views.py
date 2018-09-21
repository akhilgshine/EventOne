# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import requests
from datetime import datetime

from django.utils.crypto import get_random_string
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet

from events.models import OtpModel, EventUsers, MEMBER_CHOICES, Table, RoomType
from .serializer import OtpGenerationSerializer, OtpPostSerializer, TableListSerializer


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
        data['member_type'] = [{"id": 1, "type": "Tabler"}, {"id": 2, "type": "SqLeg"}]

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
                'id': 1,
                'name': 'Raviz',
                'event_date': '12-08 -2018',
                'Room': [
                    {
                        'id': 121,
                        'Name': 'Superior Room',
                        'Available': 5,
                        'date_from': '12-08 -2018',
                        'date_to': '13-08 -2018',
                        'rate': 2500
                    },
                    {
                        'id': 122,
                        'Name': 'Premium Room',
                        'Available': 5,
                        'date_from': '12-08 -2018',
                        'date_to': '13-08 -2018',
                        'rate': 3500
                    }
                ]
            },
            {
                'id': 2,
                'name': 'Beach',
                'event_date': '12-08 -2018',
                'Room': [
                    {
                        'id': 125,
                        'Name': 'Premium',
                        'Available': 5,
                        'date_from': '12-08 -2018',
                        'date_to': '13-08 -2018',
                        'rate': 2500
                    },

                ]
            },
                ])
