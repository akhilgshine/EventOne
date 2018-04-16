from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from events.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        print "start Mailing"

        reg_users = RegisteredUsers.objects.all()
        for user in reg_users:            
            mail = user.event_user.email
            event_obj = user
            send_email(mail,event_obj)
        print "End"

def send_email(to_email, event_obj):
    subject = 'QRT 85 Registration'
    cxt = {'event_register': event_obj }
    content = render_to_string('coupon_mail.html', cxt) 
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, 'hi', from_email, to=[to_email])
    msg.attach_alternative(content, "text/html")
    msg.send()
    print("mail to : ",str(to_email))