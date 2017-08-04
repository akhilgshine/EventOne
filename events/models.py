# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


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
	event = models.ForeignKey(Event)

	def __str__(self):
		return self.table_name


class EventUsers(models.Model):
	table = models.ForeignKey(Table)
	first_name = models.CharField(max_length=40, blank=False)
	last_name = models.CharField(max_length=40, blank=False)
	mobile = models.CharField(max_length=20, blank=True)
	email = models.CharField(max_length=30, blank=False)
	post = models.CharField(max_length=30, blank=True)

	def __str__(self):
		return self.first_name


class RegisteredUsers(models.Model):
	event_user = models.ForeignKey(EventUsers)
	event = models.ForeignKey(Event)
	payment = models.CharField(max_length=20, blank=False)
	amount_paid = models.CharField(max_length=20, blank=False, null=False)
	qrcode = models.CharField(max_length=20, blank=False, null=False)
	table = models.ForeignKey(Table)
	created_date=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.event.title


