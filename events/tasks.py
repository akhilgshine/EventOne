import base64

import os
from celery.task import Task
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
import imgkit

from events.models import RegisteredUsers
from events.utils import send_email


class CouponImageGenerate(Task):

    def run(self, id, **kwargs):
        current_site = Site.objects.get_current()
        domain = current_site.domain

        options = {
            'format': 'png',
            'encoding': "UTF-8",
        }
        url = domain + str(reverse_lazy('invoice_view', kwargs={'pk': base64.b64encode(str(id))}))
        coupon_file_name = '%s.png' % id
        imgkit.from_url(url, os.path.join(settings.BASE_DIR, 'Media', coupon_file_name), options=options)
        reg_user_obj = RegisteredUsers.objects.get(id=id)
        message = ''
        send_email(reg_user_obj.event_user.email, message, reg_user_obj)
