# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, View
from django.core.urlresolvers import reverse
from events.models import *
# Create your views here.
import json
from events.forms import *
from events.models import *
from events.utils import send_email
from django.contrib.auth import authenticate, login
import requests
from django.contrib.auth import logout

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

"""
    Login View
    """
class LoginView(View):
    template_name = "login.html"
    
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {'form':form})

    # def authenticate_user(self, username=None, password=None):
        
    #     if '@' in username:
    #         kwargs = {'email': username}
    #     else:
    #         kwargs = {'username': username}
    #     try:
    #         user = CustomUser.objects.get(**kwargs)
    #         if user.check_password(password):
    #             return user
    #     except:
    #         return None

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
            	try:
	            	if user.is_active:
	            		login(request, user)	
	            		return HttpResponseRedirect(reverse('register_event'))
            	except:
            		return render(self.request,self.template_name,{'form':form})
            else:
            	return render(self.request,self.template_name,{'form':form})



class RegisterEvent(TemplateView):
	
	template_name = 'register.html'
	
	def get(self, request, *args, **kwargs):
		context = {}
		if not request.user.is_authenticated():
			return HttpResponseRedirect(reverse('login'))

		context['form'] = EventRegisterForm()
		context['tables'] = Table.objects.all()
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):

		try:
			name = request.POST['name']
			email = request.POST['email']
			mobile = request.POST['mobile']
			table = request.POST['table_val']

			payment = request.POST['payment']
			price = request.POST['price']

			table = Table.objects.get(id=int(table))
			
			event_user, created = EventUsers.objects.get_or_create(table=table,
				first_name=name,
				email=email,
				mobile=mobile)
			if created:
				event_user.save()

			event = Event.objects.filter()[0]

			event_reg = RegisteredUsers.objects.create(event_user=event_user,
				event=event,
				payment=payment,
				amount_paid=price,
				table= table,)

			if event_reg:
				mobile = '9946341903'
				message = "Hello welcome to "
				# message_status = requests.get('http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to='+mobile+'&sender=QrtReg&message='+message)

				send_email(email,message,event_reg)

			context['event_register'] = event_reg

			return render(request, 'invoice.html', context)
		except:
			return HttpResponseRedirect(reverse('register_event'))


class GetName(TemplateView):

	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			results = []
			q = request.GET.get('term', '')
			table_name = request.GET.get('table', '')
			table = Table.objects.get(id=int(table_name))

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

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')