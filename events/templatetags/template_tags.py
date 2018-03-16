from events.models import *
from django import template

register = template.Library()


@register.filter
def get_hotel_details(user_id):
    try:
        user = RegisteredUsers.objects.get(id=user_id)
        hotel = Hotels.objects.get(registered_users=user)
        return hotel.room_type.room_type + '(' + str(hotel.checkin_date).split(" ")[0] + ' to ' + \
               str(hotel.checkout_date).split(" ")[0] + ')'
    except:
        return ''


@register.filter
def get_hotel_rent(user_id):
    try:
        user = RegisteredUsers.objects.get(id=user_id)
        hotel = Hotels.objects.get(registered_users=user)
        return hotel.tottal_rent
    except:
        return ''

# @register.filter
# def get_booked_date(user_id):
# 	try:
# 		user = RegisteredUsers.objects.get(id=user_id)
# 		hotel = Hotels.objects.get(registered_users=user)

# 			return 'Booked for 2018.08.03 and 2018.08.04'
# 		else:
# 			return 'Booked for 2018.08.03'
# 	except:
# 		return ''
