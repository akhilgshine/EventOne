# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from events.models import *

from .templatetags import *
from import_export.admin import ImportExportModelAdmin

# class EventUsersAdmin(ImportExportModelAdmin):
# 	list_display = ('first_name', 'last_name', 'mobile', 'email')

# class RegisteredUsersAdmin(ImportExportModelAdmin):
# 	list_display = ('event_user', 'table', 'event', 'amount_paid', 'event_status')

# class TableAdmin(ImportExportModelAdmin):
# 	list_display = ('table_name', 'table_order', 'event')

# Register your models here.
admin.site.register(Event)
admin.site.register(Table)


class RegisteredUserAdmin(admin.ModelAdmin):
    readonly_fields = ['get_total_paid','get_registered_amount', 'created_date']

    def get_total_paid(self, obj, *args, **kwargs):
        return str(obj.total_paid)

    def get_registered_amount(self, obj, *args, **kwargs):
        return str(obj.registered_amount)

    class Meta:
        model = RegisteredUsers


admin.site.register(RegisteredUsers, RegisteredUserAdmin)
admin.site.register(EventUsers)
admin.site.register(Hotels)
admin.site.register(RoomType)
