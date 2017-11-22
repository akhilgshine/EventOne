# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from events.models import *
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
admin.site.register(RegisteredUsers)
admin.site.register(EventUsers)
admin.site.register(Hotels)
admin.site.register(RoomType)
