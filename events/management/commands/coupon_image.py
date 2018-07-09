import os

import imgkit
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from events.models import *
from events.utils import encoded_id


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "creating coupon...."

        reg_users = RegisteredUsers.objects.all()

        current_site = Site.objects.get_current()
        domain = current_site.domain

        options = {
            'format': 'png',
            'encoding': "UTF-8",
        }

        for user in reg_users:
            url = domain + str(reverse_lazy('invoice_view', kwargs={'pk': encoded_id(user.id)}))
            coupon_file_name = '%s.png' % user.id
            imgkit.from_url(url, os.path.join(settings.BASE_DIR, 'Media', coupon_file_name), options=options)
