# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from events.models import *


class EventUsersAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'mobile', 'email')

class RegisteredUsersAdmin(admin.ModelAdmin):
	list_display = ('event_user', 'table', 'event', 'amount_paid', 'event_status')


# Register your models here.
admin.site.register(Event)
admin.site.register(Table)
admin.site.register(RegisteredUsers, RegisteredUsersAdmin)
admin.site.register(EventUsers, EventUsersAdmin)