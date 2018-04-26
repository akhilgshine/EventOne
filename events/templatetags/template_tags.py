from events.models import *
from django import template

from events.utils import encoded_id

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


@register.filter
def no_of_night(user_id):
    try:
        user = RegisteredUsers.objects.get(id=user_id)
        hotel = Hotels.objects.get(registered_users=user)
        nights = hotel.checkout_date - hotel.checkin_date
        return nights.days
    except:
        return ''


@register.filter
def payment_status(user_id):
    user = RegisteredUsers.objects.get(id=user_id)
    if user.event_user.member_type == 'Square_Leg':
        if (user.event_status == 'Stag' and user.amount_paid < 4000) or (
                user.event_status == 'Couple' and user.amount_paid < 5000):
            return 'Partial'
        elif (user.event_status == 'Stag_Informal' and user.amount_paid < 2500) or (
                user.event_status == 'Couple_Informal' and user.amount_paid < 3500):
            return 'Partial'
        else:
            return 'Complete'
    else:
        if (user.event_status == 'Not Mentioned') or (user.event_status == 'Stag' and user.amount_paid < 5000) or (
                user.event_status == 'Couple' and user.amount_paid < 6000):
            return 'Partial'
        else:
            return 'Complete'


@register.filter
def check_event_status(user_id):
    try:
        # user = RegisteredUsers.objects.get(id=user_id)
        # hotel = Hotels.objects.get(registered_users=user)
        # nights = hotel.checkout_date - hotel.checkin_date
        return True
    except:
        return False


@register.filter
def replace_(value):
    try:
        return value.replace("_", " ")
    except Exception as e:
        print(e, "Exception template tag(72) Replace '_'")
        return value


@register.filter
def completly_paid_count(count):
    users = RegisteredUsers.objects.filter(is_active=True)
    count = 0
    for user in users:
        if user.event_user.member_type == 'Square_Leg':
            if (user.event_status == 'Stag' and user.amount_paid < 4000) or (
                    user.event_status == 'Couple' and user.amount_paid < 5000):
                pass
            elif (user.event_status == 'Stag_Informal' and user.amount_paid < 2500) or (
                    user.event_status == 'Couple_Informal' and user.amount_paid < 3500):
                pass
            else:
                count = count + 1
        else:
            if (user.event_status == 'Not Mentioned') or (user.event_status == 'Stag' and user.amount_paid < 5000) or (
                    user.event_status == 'Couple' and user.amount_paid < 6000):
                pass
            else:
                count = count + 1
    return count


@register.filter
def partly_paid_count(count):
    users = RegisteredUsers.objects.filter(is_active=True)
    count = 0
    for user in users:
        if user.event_user.member_type == 'Square_Leg':
            if (user.event_status == 'Stag' and user.amount_paid < 4000) or (
                    user.event_status == 'Couple' and user.amount_paid < 5000):
                count = count + 1
            elif (user.event_status == 'Stag_Informal' and user.amount_paid < 2500) or (
                    user.event_status == 'Couple_Informal' and user.amount_paid < 3500):
                count = count + 1
            else:
                pass
        else:
            if (user.event_status == 'Not Mentioned') or (user.event_status == 'Stag' and user.amount_paid < 5000) or (
                    user.event_status == 'Couple' and user.amount_paid < 6000):
                count = count + 1
            else:
                pass
    return count


@register.filter
def get_roomtype_count(booked_room_type, date=None):
    if date:
        booked_room_type = Hotels.objects.filter(registered_users__is_active=True,
                                                 checkin_date__lte=date,
                                                 room_type=booked_room_type).count()
    else:
        booked_room_type = Hotels.objects.filter(registered_users__is_active=True, room_type=booked_room_type).count()
    return booked_room_type


@register.filter
def hotels_booked_two_nights(hotels_book_date):
    hotels_book = Hotels.objects.filter(registered_users__is_active=True, checkin_date__lte=hotels_book_date,
                                        checkout_date__gte=hotels_book_date).count()
    return hotels_book


@register.filter
def total_room_count(booked_room_type):
    obj = RoomType.objects.get(room_type=booked_room_type)
    booked_room_type = get_roomtype_count(booked_room_type) + obj.rooms_available
    return booked_room_type


@register.assignment_tag
def get_room_count(booked_room_type, date):
    obj = RoomType.objects.get(room_type=booked_room_type)
    booked_room_type = get_roomtype_count(booked_room_type, date)
    return booked_room_type


@register.assignment_tag
def encrypt_id(user_id):
    return encoded_id(user_id)
