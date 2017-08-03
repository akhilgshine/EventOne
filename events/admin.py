# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from events.models import *

# Register your models here.
admin.site.register(Event)
admin.site.register(Table)
admin.site.register(RegisteredUsers)
admin.site.register(EventUsers)