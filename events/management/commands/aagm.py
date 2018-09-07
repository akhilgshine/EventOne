import csv
import re

from django.core.management.base import BaseCommand, CommandError

from events.models import EventUsers, RegisteredUsers, Table, Event
from events.utils import send_sms_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "start"
        f = open('csv_tables/aagm.csv', 'r')
        data = csv.reader(f)
        print data

        for indx, row in enumerate(data):

            if indx == 0:
                print ("Header")
                continue
            print(row)
            type = row[0]
            name = row[1]
            table = row[2]
            qrcode = row[3]
            amount = row[4]
            payment_method = row[5]
            namelist = name.split(' ', 1)
            if len(namelist) == 2:
                first_name = namelist[0]
                last_name = namelist[1]
            else:
                first_name = namelist[0]
                last_name = ''

            event = Event.objects.filter()
            if len(event) > 0:
                event = event[0]
            else:
                event = Event.objects.create(title='Area 1Agm of Roundable India for the year 2018',
                                             description='Area 1Agm of Roundable India for the year 2018 Lets go nuts hosted at Qrt 85 at Kollam. Count down starts here',
                                             price=2000)
            try:
                table = Table.objects.get(table_name=table)
            except Table.DoesNotExist:
                print "Table not found error %s" % table

            try:
                event_user = EventUsers.objects.get(member_type=type,
                                                    table=table,
                                                    first_name=first_name,
                                                    last_name=last_name)

            except EventUsers.DoesNotExist:
                event_user = EventUsers.objects.get(member_type=type,
                                                    table=table,
                                                    first_name=first_name)

            event_reg, created = RegisteredUsers.objects.get_or_create(event=event, event_user=event_user,
                                                                       amount_paid=amount, table=table,
                                                                       payment=payment_method)

            message = "You are successfully registered for the event, " \
                      "Area 1 Agm of Round Table India  'Black and White'." \
                      " And you have paid Rs.%s/-" % (str(event_reg.amount_paid))
            # send_sms_message(event_reg.event_user.mobile, message, event_reg.id)
            print(message)
