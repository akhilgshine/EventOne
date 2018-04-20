# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from events.models import *

class RegisteredUserAdmin(admin.ModelAdmin):

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
        model = Hotels


class BookedHotelAdmin(ImportExportModelAdmin):

    search_fields = ['registered_users__event_user__first_name', 'registered_users__event_user__last_name']
    resource_class = BookedHotelResource

    class Meta:
        model = Hotels


admin.site.register(RegisteredUsers, RegisteredUserAdmin)
admin.site.register(EventUsers)
admin.site.register(Hotels, BookedHotelAdmin)
admin.site.register(RoomType)
admin.site.register(Event)
admin.site.register(Table)
