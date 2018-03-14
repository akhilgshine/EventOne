# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

STATUS_CHOICES = (
    ('Couple', _('Couple')),
    ('Stag', _('Stag')),
    ('Not Mentioned', _('Not Mentioned')),
)

ROOM_CHOICES = (
    ('Single', _('Single')),
    ('Double', _('Double')),
    ('Deluxe', _('Deluxe')),
)


class Event(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    event_image = models.ImageField(upload_to='event_images/', blank=True)
    price = models.IntegerField(blank=True)
    total_seats = models.IntegerField(blank=False, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Table(models.Model):
    table_name = models.CharField(max_length=30, blank=True, null=True)
    table_order = models.IntegerField(blank=True, null=True)
    event = models.ForeignKey(Event)

    def __str__(self):
        return self.table_name


class EventUsers(models.Model):
    table = models.ForeignKey(Table)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    mobile = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=100, blank=False)
    post = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.first_name


class RegisteredUsers(models.Model):
    event_user = models.ForeignKey(EventUsers)
    event = models.ForeignKey(Event)
    payment = models.CharField(max_length=20, blank=False)
    amount_paid = models.IntegerField(blank=True, null=True)
    qrcode = models.CharField(max_length=20, blank=False, null=False)
    table = models.ForeignKey(Table)
    created_date = models.DateTimeField(auto_now_add=True)
    confirm_image = models.ImageField(upload_to='confirm_images/', blank=True)
    event_status = models.CharField(choices=STATUS_CHOICES, max_length=30, blank=True, null=True)
    balance_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.event.title


class PaymentDetails(models.Model):
    reg_event = models.ForeignKey(RegisteredUsers, null=True)
    amount = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)


class RoomType(models.Model):
    room_type = models.CharField(max_length=50, null=True)
    rooms_available = models.IntegerField(blank=True, null=True)
    net_rate = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.room_type


class Hotels(models.Model):
	registered_users = models.ForeignKey(RegisteredUsers,null=True,related_name='hotel')
	hotel_name = models.CharField(max_length=50,null=True)
	room_number = models.CharField(max_length=20,null=True)
	tottal_rent = models.IntegerField(blank=True, null=True)	
	# room_type = models.CharField(choices=ROOM_CHOICES,max_length=30,null=True,blank=True)
	book_friday = models.BooleanField(default=False)
	room_type = models.ForeignKey(RoomType,null=True,blank=True)
	checkin_date = models.DateTimeField(null=True, blank=True)
	checkout_date = models.DateTimeField(null=True, blank=True)
	
	def __str__(self):
		return self.hotel_name
