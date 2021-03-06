# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import datetime

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from events.tasks import CouponImageGenerate

CASH = 'cash'
POS = 'POS'
CARD = 'card'
BANK_TRANSFER = 'bank_transfer'
CHEQUE = 'cheque'

STATUS_CHOICES = (
    ('Couple', _('Couple')),
    ('Stag', _('Stag')),
    ('Couple_Informal', _('Couple(1 Day)')),
    ('Stag_Informal', _('Stag(1 Day)')),
    ('Not_Mentioned', _('Not Mentioned')),
)
ROOM_CHOICES = (
    ('Single', _('Single')),
    ('Double', _('Double')),
    ('Deluxe', _('Deluxe')),
)
MEMBER_CHOICES = (
    ('Tabler', _('Tabler')),
    ('Square_Leg', _('Square Leg'))
)

PAYMENT_CHOICES = (
    (CASH, _("Cash")),
    (POS, _("POS")),
    (CARD, _("Card")),
    (BANK_TRANSFER, _("Bank Transfer")),
    (CHEQUE, _("Cheque")),
)

EVENT_REGISTER = 0
STATUS_UPGRADE = 1
REG_DUE_PAYMENT = 2
HOTEL_BOOKING = 3
HOTEL_UPDATE = 4
HOTEL_DUE_PAYMENT = 5
OTHER_CONTRIBUTIONS = 6

TYPE_CHOICES = (
    (EVENT_REGISTER, ('Event Registered')),
    (STATUS_UPGRADE, ('Status Upgrade')),
    (REG_DUE_PAYMENT, 'Reg Due Payment'),
    (HOTEL_BOOKING, ('Hotel Booking')),
    (HOTEL_UPDATE, ('Hotel Update Booking')),
    (HOTEL_DUE_PAYMENT, ('Hotel Due Payment')),
    (OTHER_CONTRIBUTIONS, ('Other Contributions')),
)
SMALL = 'S'
LARGE = 'L'
MEDIUM = 'M'
EXTRA_LARGE = 'XL'
DOUBLE_EXTRA_LARGE = 'XXL'

T_SHIRT_CHOICES = (
    (SMALL, ('S')),
    (LARGE, ('L')),
    (MEDIUM, ('M')),
    (EXTRA_LARGE, ('XL')),
    (DOUBLE_EXTRA_LARGE, ('XXL')),
)

STAG = 'Stag'
COUPLE = 'Couple'
KID = 'Kid'
EXTRA_PERSON = 'Extra_Person'

FRIDAY_USER_TYPE_CHOICES = (
    (STAG, 'Stag'),
    (COUPLE, 'Couple'),
    (KID, 'Kid'),
    (EXTRA_PERSON, 'Extra Person')

)
FRIDAY = 'Friday'
SATURDAY = 'Saturday'
SUNDAY = 'Sunday'

DAY_TYPE_CHOICES = (

    (FRIDAY, 'Friday'),
    (SATURDAY, 'Saturday'),
    (SUNDAY, 'Sunday'),
)

LUNCH = 'Lunch'
DINNER = 'Dinner'

TIME_TYPE_CHOICES = (
    (LUNCH, 'Lunch'),
    (DINNER, 'Dinner'),
)


class Event(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    event_image = models.ImageField(upload_to='event_images/', blank=True)
    price = models.IntegerField(blank=True)
    total_seats = models.IntegerField(blank=False, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return self.title


class Hotel(models.Model):
    """
    Model to save hotel details
    """
    name = models.CharField(max_length=255)
    publish = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotels'


class Table(models.Model):
    table_name = models.CharField(max_length=30, blank=True, null=True)
    table_order = models.IntegerField(blank=True, null=True)
    event = models.ForeignKey('events.Event')
    is_partial_payment = models.BooleanField(default=True)

    def __str__(self):
        return self.table_name


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class EventUsers(AbstractBaseUser, PermissionsMixin):
    member_type = models.CharField(choices=MEMBER_CHOICES, max_length=50, default='Tabler')
    table = models.ForeignKey('events.Table', null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    mobile = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=100, blank=False, unique=True)
    post = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def registered_obj(self):
        try:
            return self.get_user_registration.all()[0]
        except IndexError:
            return None

    class Meta:
        verbose_name = 'Event User'
        verbose_name_plural = 'Event Users'

    def __str__(self):
        return self.get_full_name()


class OtpModel(models.Model):
    mobile = models.CharField(max_length=15, default=0)
    created_time = models.DateTimeField(default=datetime.datetime.now, blank=True)
    otp = models.CharField(max_length=25, unique=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.otp


class RegisteredUsers(models.Model):
    event_user = models.ForeignKey('events.EventUsers', related_name='get_user_registration')
    event = models.ForeignKey('events.Event')
    payment = models.CharField(choices=PAYMENT_CHOICES, max_length=20, blank=False)
    amount_paid = models.IntegerField(blank=True, null=True)
    qrcode = models.CharField(max_length=20, blank=False, null=False)
    table = models.ForeignKey('events.Table')
    created_date = models.DateTimeField(auto_now_add=True)
    confirm_image = models.ImageField(upload_to='confirm_images/', blank=True)
    event_status = models.CharField(choices=STATUS_CHOICES, max_length=30, blank=True, null=True)
    balance_amount = models.IntegerField(blank=True, null=True)
    reciept_number = models.CharField(blank=True, null=True, max_length=100)
    reciept_file = models.FileField(blank=True, null=True, upload_to='reciepts')
    contributed_amount = models.IntegerField(default=0)
    t_shirt_size = models.CharField(choices=T_SHIRT_CHOICES, max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_payment_completed = models.BooleanField(default=False)
    is_attending_event = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.event_user.first_name, self.event_user.last_name)

    class Meta:
        verbose_name = 'Registered User'
        verbose_name_plural = 'Registered Users'

    @property
    def total_paid(self):
        if not self.amount_paid:
            self.amount_paid = 0
        rent = 0
        if self.hotel.all():
            rent = self.hotel.all().aggregate(total=Sum("tottal_rent"))["total"]
        if not rent:
            rent = 0

        if not self.contributed_amount:
            self.contributed_amount = 0
        return self.amount_paid + int(rent) + int(self.contributed_amount)

    @property
    def hotel_name(self):
        if self.hotel.all():
            hotel = self.hotel.all()[0].hotel_name
            return hotel

    @property
    def hotel_room_type(self):
        if self.hotel.all():
            room_type = self.hotel.all()[0].room_type
            return room_type

    @property
    def checkin_date(self):
        if self.hotel.all():
            checkin_date = self.hotel.all()[0].checkin_date
            return checkin_date

    @property
    def checkout_date(self):
        if self.hotel.all():
            checkout_date = self.hotel.all()[0].checkout_date
            return checkout_date

    @property
    def registered_amount(self):
        if self.event_user.member_type == 'Tabler':
            if self.event_status == 'Stag':
                return 5000
            return 6000
        else:
            if self.event_status == 'Stag':
                return 4000
            elif self.event_status == 'Couple':
                return 5000
            elif self.event_status == 'Stag_Informal':
                return 2500
            return 3500

    # @property
    # def contributed_amount(self):
    #     return self.amount_paid - self.registered_amount
    @property
    def due_amount(self):
        amount = 0 if self.registered_amount - (
            0 if self.amount_paid is None else self.amount_paid) < 0 else self.registered_amount - (
            0 if self.amount_paid is None else self.amount_paid)
        return amount

    @property
    def hotel_rent(self):
        if self.hotel.all():
            if self.hotel.all()[0].room_type:
                hotel_rent = self.hotel.all()[0].room_type.net_rate
                checkout = self.hotel.all()[0].checkout_date
                checkin = self.hotel.all()[0].checkin_date
                if checkin and checkout:
                    difference = checkout - checkin
                else:
                    return 0
                return hotel_rent * difference.days
        return 0

    @property
    def hotel_due(self):
        if self.hotel.all():
            if not self.id in [94, 18, 100, 20]:
                return self.hotel_rent - self.hotel.all()[0].tottal_rent
            return 0
        return 0

    @property
    def total_due(self):
        due = 0
        if self.hotel_due:
            due = self.hotel_due
        return self.due_amount + due

    @property
    def hotel_user(self):
        try:
            return self.hotel.all()[0]
        except IndexError:
            return None

    @property
    def friday_coupon_amount(self):
        if self.get_coupon_purchase.all():
            return self.get_coupon_purchase.all().aggregate(Sum('total_amount_paid')).get(
                'total_amount_paid__sum')
        return 0

    @property
    def encoded_id(self):
        return base64.b64encode(str(self.id))


class PaymentDetails(models.Model):
    reg_event = models.ForeignKey('events.RegisteredUsers', null=True)
    amount = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, blank=True, null=True)
    mode_of_payment = models.CharField(choices=PAYMENT_CHOICES, max_length=50, blank=True, null=True)
    receipt_number = models.CharField(blank=True, null=True, max_length=100)
    receipt_file = models.FileField(blank=True, null=True, upload_to='payment_receipts')

    def __str__(self):
        return "{} {}".format(self.reg_event.event_user.first_name, self.reg_event.event_user.last_name)

    class Meta:
        verbose_name = 'User Payment Detail'
        verbose_name_plural = 'User Payment Details'


class RoomType(models.Model):
    hotel = models.ForeignKey('events.Hotel', related_name='get_hotel_room_types')
    room_type = models.CharField(max_length=50, null=True)
    rooms_available = models.IntegerField(blank=True, null=True)
    net_rate = models.IntegerField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.room_type

    class Meta:
        ordering = ['sort_order', ]


class ImageRoomType(models.Model):
    image = models.ImageField(upload_to='room_type_images')
    room_type = models.ForeignKey('events.RoomType', null=True, related_name='get_room_type_image')

    def __str__(self):
        return self.room_type.room_type


class BookedHotel(models.Model):
    registered_users = models.ForeignKey('events.RegisteredUsers', null=True, related_name='hotel')
    hotel = models.ForeignKey('events.Hotel')
    room_number = models.CharField(max_length=20, null=True, blank=True)
    tottal_rent = models.IntegerField(default=0)
    book_friday = models.BooleanField(default=False)
    room_type = models.ForeignKey('events.RoomType', null=True, blank=True)
    checkin_date = models.DateTimeField(null=True, blank=True)
    checkout_date = models.DateTimeField(null=True, blank=True)
    booked_date = models.DateTimeField(default=datetime.datetime.now, blank=True)
    mode_of_payment = models.CharField(choices=PAYMENT_CHOICES, max_length=30, blank=True, null=True)
    receipt_number = models.CharField(blank=True, null=True, max_length=100)
    receipt_file = models.FileField(blank=True, null=True, upload_to='hotel_receipts')

    def __str__(self):
        return "{} {}".format(self.registered_users.event_user.first_name,
                              self.registered_users.event_user.last_name)

    @property
    def hotel_name(self):
        return self.hotel.name


class ProxyHotelBooking(models.Model):
    table = models.ForeignKey('events.Table', null=True, blank=True)
    hotel = models.ForeignKey('events.Hotel')
    room_type = models.ForeignKey('events.RoomType', null=True, blank=True)
    hotel_rent = models.IntegerField(default=0)
    check_in_date = models.DateTimeField(null=True, blank=True)
    check_out_date = models.DateTimeField(null=True, blank=True)
    booked_date = models.DateTimeField(default=datetime.datetime.now, blank=True)

    def __str__(self):
        return self.table.table_name


class EventDocument(models.Model):
    description = models.CharField(max_length=255, null=True, blank=True)
    event_videos = models.FileField(upload_to='event_videos/', null=True, blank=True)
    event_images = models.ImageField(upload_to='event_images/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.description)


class IDDocumentsPhoto(models.Model):
    registered_users = models.ForeignKey('events.RegisteredUsers', related_name='ids_img')
    id_card_type = models.CharField(max_length=255, null=True, blank=True)
    id_card_images = models.ImageField(upload_to='id_card_images/', null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.registered_users.event_user.first_name, self.registered_users.event_user.last_name)


@receiver(post_save, sender='events.RegisteredUsers', dispatch_uid="create_coupon")
def create_coupon(sender, instance, **kwargs):
    CouponImageGenerate.delay(instance.id)


@receiver(post_save, sender='events.BookedHotel', dispatch_uid="create_hotel_update_coupon")
def create_hotel_update_coupon(sender, instance, **kwargs):
    CouponImageGenerate.delay(instance.registered_users.id)


@receiver(post_delete, sender='events.BookedHotel')
def increment_roomtype(instance, **kwargs):
    if instance.room_type:
        instance.room_type.rooms_available += 1
        instance.room_type.save()


class FoodType(models.Model):
    day = models.CharField(choices=DAY_TYPE_CHOICES, max_length=255, null=True, blank=True)
    time = models.CharField(choices=TIME_TYPE_CHOICES, max_length=255, null=True, blank=True)

    def __str__(self):
        return '{}, {}'.format(self.day, self.time)


class UserFoodCoupon(models.Model):
    coupon_user = models.ForeignKey('events.RegisteredUsers', null=True, blank=True,
                                    related_name='get_all_food_type_coupons')
    type = models.ForeignKey('events.FoodType', null=True, blank=True)
    is_used = models.BooleanField(default=False)
    used_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.coupon_user.event_user.first_name, self.coupon_user.event_user.last_name)


class CouponPurchase(models.Model):
    registered_users = models.ForeignKey('events.RegisteredUsers', null=True, blank=True,
                                         related_name='get_coupon_purchase')
    adult_friday_lunch = models.IntegerField(default=0)
    kids_friday_lunch = models.IntegerField(default=0)
    kids_coupon = models.IntegerField(default=0)
    no_of_extra_persons = models.IntegerField(default=0)
    total_amount_paid = models.IntegerField(default=0)
    payment_mode = models.CharField(choices=PAYMENT_CHOICES, max_length=30, blank=True, null=True)
    purchase_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.registered_users.event_user.first_name, self.registered_users.event_user.last_name)


class FridayDinnerAmount(models.Model):
    user_type = models.CharField(max_length=255, choices=FRIDAY_USER_TYPE_CHOICES, null=True, blank=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.user_type


class KidsCouponAmount(models.Model):
    amount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.amount)


class PartialPayment(models.Model):
    registered_users = models.ForeignKey('events.RegisteredUsers', null=True, blank=True,
                                         related_name='get_partial_payment')
    amount_due = models.CharField(max_length=255, null=True, blank=True)
    mode_of_payment = models.CharField(choices=PAYMENT_CHOICES, max_length=30, blank=True, null=True)
    receipt_number = models.CharField(blank=True, null=True, max_length=100)
    receipt_file = models.FileField(blank=True, null=True, upload_to='payment_reciepts')

    def __str__(self):
        return '{} {}'.format(self.registered_users.event_user.first_name, self.registered_users.event_user.last_name)


class ProgramSchedule(models.Model):
    program_name = models.CharField(max_length=255, null=True, blank=True)
    program_theme = models.CharField(max_length=255, null=True, blank=True)
    dress_code = models.CharField(max_length=255, null=True, blank=True)
    program_description = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    program_time_from = models.DateTimeField(null=True, blank=True)
    program_time_to = models.DateTimeField(null=True, blank=True)
    extra_information = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.program_name)


class PinCoupon(models.Model):
    registered_users = models.ForeignKey('events.RegisteredUsers', null=True, blank=True,
                                         related_name='get_pin_amount')
    amount = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.registered_users.event_user.first_name, self.registered_users.event_user.last_name)
