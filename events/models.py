# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Sum
from datetime import datetime
from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

CASH = 'cash'
POS = 'POS'
CARD = 'card'
BANK_TRANSFER = 'bank_transfer'

STATUS_CHOICES = (
    ('Couple', _('Couple')),
    ('Stag', _('Stag')),
    ('Couple_Informal', _('Couple Informal')),
    ('Stag_Informal', _('Stag Informal')),
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


class Event(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    event_image = models.ImageField(upload_to='event_images/', blank=True)
    price = models.IntegerField(blank=True)
    total_seats = models.IntegerField(blank=False, null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return self.title


class Table(models.Model):
    table_name = models.CharField(max_length=30, blank=True, null=True)
    table_order = models.IntegerField(blank=True, null=True)
    event = models.ForeignKey(Event)

    def __str__(self):
        return self.table_name


class EventUsers(models.Model):
    member_type = models.CharField(choices=MEMBER_CHOICES, max_length=50, default='Tabler')
    table = models.ForeignKey(Table)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    mobile = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=100, blank=False)
    post = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = 'Event User'
        verbose_name_plural = 'Event Users'


class RegisteredUsers(models.Model):
    event_user = models.ForeignKey(EventUsers)
    event = models.ForeignKey(Event)
    payment = models.CharField(choices=PAYMENT_CHOICES, max_length=20, blank=False)
    amount_paid = models.IntegerField(blank=True, null=True)
    qrcode = models.CharField(max_length=20, blank=False, null=False)
    table = models.ForeignKey(Table)
    created_date = models.DateTimeField(auto_now_add=True)
    confirm_image = models.ImageField(upload_to='confirm_images/', blank=True)
    event_status = models.CharField(choices=STATUS_CHOICES, max_length=30, blank=True, null=True)
    balance_amount = models.IntegerField(blank=True, null=True)
    reciept_number = models.CharField(blank=True, null=True, max_length=100)
    reciept_file = models.FileField(blank=True, null=True, upload_to='reciepts')
    contributed_amount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

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
        return 0 if self.registered_amount - self.amount_paid < 0 else self.registered_amount - self.amount_paid

    @property
    def hotel_rent(self):
        if self.hotel.all():
            if self.hotel.all()[0].room_type:
                hotel_rent = self.hotel.all()[0].room_type.net_rate
                checkout = self.hotel.all()[0].checkout_date
                checkin = self.hotel.all()[0].checkin_date
                difference = checkout - checkin
                return hotel_rent * difference.days
        return 0

    @property
    def hotel_due(self):
        if self.hotel.all():
            return self.hotel_rent - self.hotel.all()[0].tottal_rent
        return 0

    @property
    def total_due(self):
        due = 0
        if self.hotel_due:
            due = self.hotel_due
        return self.due_amount + due


class PaymentDetails(models.Model):
    reg_event = models.ForeignKey(RegisteredUsers, null=True)
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
    room_type = models.CharField(max_length=50, null=True)
    rooms_available = models.IntegerField(blank=True, null=True)
    net_rate = models.IntegerField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.room_type

    class Meta:
        ordering = ['sort_order', ]

    @receiver(post_delete, sender='events.Hotels')
    def increment_roomtype(instance, **kwargs):
        instance.room_type.rooms_available += 1
        instance.room_type.save()


class Hotels(models.Model):
    registered_users = models.ForeignKey(RegisteredUsers, null=True, related_name='hotel')
    hotel_name = models.CharField(max_length=50, null=True)
    room_number = models.CharField(max_length=20, null=True)
    tottal_rent = models.IntegerField(default=0)
    book_friday = models.BooleanField(default=False)
    room_type = models.ForeignKey(RoomType, null=True, blank=True)
    checkin_date = models.DateTimeField(null=True, blank=True)
    checkout_date = models.DateTimeField(null=True, blank=True)
    booked_date = models.DateTimeField(default=datetime.now, blank=True)
    mode_of_payment = models.CharField(choices=PAYMENT_CHOICES, max_length=30, blank=True, null=True)
    receipt_number = models.CharField(blank=True, null=True, max_length=100)
    receipt_file = models.FileField(blank=True, null=True, upload_to='hotel_receipts')

    def __str__(self):
        return "{} {}".format(self.registered_users.event_user.first_name,
                              self.registered_users.event_user.last_name)

    class Meta:
        verbose_name = 'Booked Hotel'
        verbose_name_plural = 'Booked Hotels'
