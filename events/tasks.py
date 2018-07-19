import base64

import os

import time
from celery.task import Task
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import imgkit

from django.apps import apps

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
        time.sleep(2)
        registered_user_model = apps.get_model('events', 'RegisteredUsers')

        reg_user_obj = registered_user_model.objects.get(id=id)

        message = ''
        to_email = reg_user_obj.event_user.email
        print('success',reg_user_obj.event_user.email)

        cxt = {'event_register': reg_user_obj}

        # if event_obj.amount_paid < 5000:
        # 	cxt['partial'] = 'Partial'

        subject = 'QRT 85 Registration'
        content = render_to_string('coupon_second.html', cxt)

        from_email = settings.DEFAULT_FROM_EMAIL
        print(from_email)
        msg = EmailMultiAlternatives(subject, 'Hi', from_email, to=[to_email, 'registration@letsgonuts2018.com'])
        msg.attach_alternative(content, "text/html")
        msg.send()


