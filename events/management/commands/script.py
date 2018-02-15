# ================================================================= #
# Conjob to close a conversation if the user doesn't respond for
# more than 30 minutes .
# ================================================================= #



from django.core.management.base import BaseCommand, CommandError
# from django.utils import timezone
from events.models import *
# from datetime import datetime, timedelta
import csv
import re


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "start"
        f = open('csv_tables/csv.csv', 'r')
        data = csv.reader(f)

        event = Event.objects.filter();
        if len(event) > 0:
            event = event[0]
        else:
            event = Event.objects.create(title='Area 1Agm of Roundable India for the year 2018',
                                         description='Area 1Agm of Roundable India for the year 2018 Lets go nuts hosted at Qrt 85 at Kollam. Count down starts here',
                                         price=2000)

        for indx, row in enumerate(data):
            if indx == 0:
                print ("Header")
                continue

            namelist = row[1].split(' ', 1)
            if len(namelist) == 2:
                first_name = namelist[0]
                last_name = namelist[1]
            else:
                first_name = row[1]
                last_name = ''

            if first_name and row[2] and row[3]:
                print("Data")
                table, created = Table.objects.get_or_create(table_name=row[0], event=event)

                try:
                    table_order = int(re.search(r'\d+', row[0]).group())
                    table.table_order = table_order
                    print (row[0], table_order)
                    table.save()
                except:
                    table.table_order = ''
                    table.save()

                users, created = EventUsers.objects.get_or_create(table=table,
                                                                  first_name=first_name,
                                                                  last_name=last_name,
                                                                  mobile=row[2],
                                                                  email=row[3],
                                                                  post=row[4], )
                # table, created = Table.objects.get_or_create(table_name='other',event=event)
            else:
                print ("Empty Data")
                continue
