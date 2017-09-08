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

class Event(models.Model):
	title = models.CharField(max_length=100, blank=True, null=True)
	description = models.TextField()
	event_image = models.ImageField(upload_to='event_images/', blank=True)
	price = models.IntegerField(blank=True)
	total_seats = models.IntegerField(blank=False, null=True)

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
	event_user = models.ForeignKey(EventUsers)
	amount = models.CharField(max_length=20)
	created_date = models.DateTimeField(auto_now_add=True)
		
