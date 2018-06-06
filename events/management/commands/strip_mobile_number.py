from django.core.management.base import BaseCommand, CommandError
# from django.utils import timezone
from events.models import *
from events.utils import send_sms_message, send_email


class Command(BaseCommand):

    def handle(self, *args, **options):
        print ("start")
        event_users = EventUsers.objects.all()
        for event_user in event_users:
            mobile = event_user.mobile
            event_user.mobile = mobile[-10:]
            event_user.save()
            print ("end")

