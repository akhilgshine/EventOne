from django.core.management.base import BaseCommand

from events.models import RegisteredUsers


class Command(BaseCommand):

    def handle(self, *args, **options):
        print ("start")
        registered_users = RegisteredUsers.objects.all()
        for user in registered_users:
            latest_qrcode = RegisteredUsers.objects.latest('qrcode').qrcode
            if not latest_qrcode:
                user.qrcode = '1000'
                user.save()
            else:
                current_qrcode = latest_qrcode
                new_qr_code = int(current_qrcode) + 1
                user.qrcode = new_qr_code
            user.save()
