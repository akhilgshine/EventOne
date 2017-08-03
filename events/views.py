# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, View

from events.models import *
# Create your views here.
import json
from events.forms import *
from events.models import *
from events.utils import send_email

class IndexPage(TemplateView):

	template_name = 'index.html'
	def get_context_data(self, **kwargs):

		context = super(IndexPage, self).get_context_data(**kwargs)

		context['events'] = Event.objects.filter()[:1]
		context['tables'] = Table.objects.all()
		return context


	# def post(self, request, *args, **kwargs):
	# 	try:
	# 		name = request.POST['name']
	# 		email = request.POST['email']

	# 		table = request.POST['table']
	# 		payment = request.POST['payment']

	# 		event = Event.objects.filter()[0]
	# 		table = Table.objects.get(id=table)
	# 		try:
	# 			user = User.objects.get(username=name,email=email)
	# 		except:
	# 			user = User.objects.create(username=name,
	# 				email=email,
	# 				password='pswd4321')
			
	# 		register = Registered.objects.create(user=user,
	# 			event=event,
	# 			payment=payment,
	# 			table=table)
	# 		send_email(str(email),event.title, event.event_date)
	# 	except:
	# 		print "exception"
	# 	return HttpResponseRedirect('')


class RegisterEvent(TemplateView):
	
	template_name = 'register.html'
	
	def get(self, request, *args, **kwargs):
		context = {}
		if not request.user.is_authenticated():
			return render(request, 'login.html', context)

		context['tables'] = Table.objects.all()
		return render(request, self.template_name, context)


class GetName(TemplateView):

	def get(self, request, *args, **kwargs):

		if request.is_ajax():
			results = []
			
			q = request.GET.get('term', '')
			table_name = request.GET.get('table', '')
			table = Table.objects.get(table_name=str(table_name))

			print("table : ", table)			
			users = EventUsers.objects.filter(table = table)

			print(users)
			users = users.filter(first_name__icontains=q)
			for user in users:
				user_json = {}
				user_json['id'] = user.id
				user_json['label'] = user.first_name
				user_json['value'] = user.first_name
				results.append(user_json)

			data = json.dumps(results)

			mimetype = 'application/json'
			return HttpResponse(data , mimetype)


class GetUserData(TemplateView):

    def get(self, request):
    	data = {}
    	django_messages = []
    	try:
    		username = request.GET['username']

    		user = EventUsers.objects.get(first_name=username)
    		data['email'] = user.email
    		data['mobile'] = user.mobile
    		return HttpResponse(json.dumps(data), content_type='application/json')
    	except:
    		data['success'] = "False"
    		data['error_msg'] = "something went WRONG"
    		return HttpResponse(json.dumps(data), content_type='application/json')

    	return HttpResponse(json.dumps(data), content_type='application/json')
