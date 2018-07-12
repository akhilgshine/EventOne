# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from events.models import *


class RegisteredUserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['event_user',
                    'get_registered_amount',
                    'get_due_amount',
                    'get_hotel_rent',
                    'get_hotel_due',
                    'get_total_paid',
                    'get_total_due',

                    ]

    readonly_fields = ['get_total_paid',
                       'get_registered_amount',
                       'created_date',
                       'get_hotel_rent']

    list_filter = ['payment']

    search_fields = ['event_user__first_name', 'event_user__last_name']

    def get_total_paid(self, obj, *args, **kwargs):
        return str(obj.total_paid)

    def get_registered_amount(self, obj, *args, **kwargs):
        return str(obj.registered_amount)

    def get_hotel_rent(self, obj, *args, **kwargs):
        return str(obj.hotel_rent)

    def get_due_amount(self, obj, *args, **kwargs):
        return str(obj.due_amount)

    def get_hotel_due(self, obj, *args, **kwargs):
        return str(obj.hotel_due)

    def get_total_due(self, obj, *args, **kwargs):
        return str(obj.total_due)

    class Meta:
        model = RegisteredUsers


class BookedHotelResource(resources.ModelResource):
    class Meta:
        model = BookedHotel


class BookedHotelAdmin(ImportExportModelAdmin):
    list_display = ['registered_users', 'room_type', 'tottal_rent', 'checkin_date', 'checkout_date']
    search_fields = ['registered_users__event_user__first_name', 'registered_users__event_user__last_name']
    resource_class = BookedHotelResource
    list_filter = ['room_type__room_type', 'registered_users__event_user__table__table_name']

    class Meta:
        model = BookedHotel


class RoomTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['room_type', 'sort_order']
    list_editable = ['sort_order']


class PaymentDetailsAdmin(ImportExportModelAdmin):
    list_display = ['reg_event', 'amount', 'created_date', 'get_type_display', 'mode_of_payment']

    class Meta:
        model = PaymentDetails


class EventUserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    class Meta:
        model = EventUsers

    search_fields = ['first_name', 'last_name', 'email', 'mobile']


class ImageRoomTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    class Meta:
        model = ImageRoomType

    search_fields = ['first_name', 'last_name', 'email', 'mobile']


class NfcCouponAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    class Meta:
        model = NfcCoupon

    search_fields = ['card_number']
    list_display = ['registered_user', 'card_number', 'created_date']


admin.site.register(RegisteredUsers, RegisteredUserAdmin)
admin.site.register(EventUsers, EventUserAdmin)
admin.site.register(BookedHotel, BookedHotelAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(Event)
admin.site.register(Table)
admin.site.register(PaymentDetails, PaymentDetailsAdmin)
admin.site.register(OtpModel)
admin.site.register(Hotel)
admin.site.register(ImageRoomType, ImageRoomTypeAdmin)
admin.site.register(ProxyHotelBooking)
admin.site.register(EventDocument)
admin.site.register(NfcCoupon, NfcCouponAdmin)
admin.site.register(FridayLunchAmount)
admin.site.register(FridayLunchBooking)
admin.site.register(IDDocumentsPhoto)
