from django.core.management.base import BaseCommand

from events.models import RegisteredUsers
from events.utils import create_user_coupon_set


class Command(BaseCommand):

    def handle(self, *args, **options):
        print 'start'
        registered_user = RegisteredUsers.objects.all().filter(created_date__lt='2018-08-01')
        for users in registered_user:
            if users.event_status == 'Couple' or users.event_status == 'Couple_Informal':
                [create_user_coupon_set(users.id) for _ in range(2)]
            else:
                create_user_coupon_set(users.id)
        print 'end'
