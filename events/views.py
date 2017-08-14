# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, View
from django.core.urlresolvers import reverse
from django.contrib import messages
from events.models import *
# Create your views here.
import json
from events.forms import *
from events.models import *
from events.utils import send_email, set_status
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

	def check_balance(self, amount):

		balance_amount = 0
		if int(amount) < 5000:
			balance_amount = 5000 - int(amount)
			if balance_amount > 0:
				return balance_amount
		return 0

	def post(self, request, *args, **kwargs):
		context = {}
		message = ''

		try:
			name = request.POST.get('first_name', '')
			last_name = request.POST.get('last_name', '')
			email = request.POST.get('email', '')
			phone = request.POST.get('phone', '')
			table = request.POST.get('table_val', '')

			payment = request.POST.get('payment', '')
			amount_paid = request.POST.get('amount_paid', '')

			event = Event.objects.filter()[0]

			try:
				new_table = request.POST.get('other_table', '')
				
				if not new_table:
					new_table = request.POST.get('table_val', '')
			except:
				new_table = ''

			if new_table:
				table, created = Table.objects.get_or_create(table_name=new_table,
					event=event)				
			else:
				table = Table.objects.get(table_name=table)

			event_user, created = EventUsers.objects.get_or_create(table=table,
				email=email)

			if created:
				event_user.first_name = name
				event_user.last_name = last_name
				event_user.mobile = phone
				event_user.save()

			qrcode = 'QRT001'

			try:
				event_reg, created = RegisteredUsers.objects.get_or_create(event_user=event_user,
					event=event,
					table= table)

				if created:
					print("amount_paid : ", amount_paid)
					balance_amount = self.check_balance(amount_paid)

					event_reg.payment = payment
					event_reg.amount_paid = amount_paid
					event_reg.balance_amount = balance_amount
					event_reg.qrcode = qrcode + str(event_reg.id)
					event_reg.save()

				else:
					
					last_pay = event_reg.amount_paid
					tottal_paid = int(last_pay) + int(amount_paid)

					balance_amount = self.check_balance(tottal_paid)
					event_reg.payment = payment
					event_reg.amount_paid = tottal_paid
					event_reg.balance_amount = balance_amount
					event_reg.save()


			except Exception as e:

				if created and event_reg:
					event_reg.delete()				
				event_reg = None

			if event_reg:
				set_status(event_reg)
				message = "You are successfully registered for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : "+event_reg.qrcode+ " And you have paid Rs."+str(event_reg.amount_paid)+"/-"
				message_status = requests.get('http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to='+phone+'&sender=QrtReg&message='+message)

				# send_email(email,message,event_reg)
				try:
					send_email(email,message,event_reg)
				except:
					pass
				# try:
				# 	send_email(email,message,event_reg )
				# except:
				# 	pass
				context['event_register'] = event_reg
				return render(request, 'invoice.html', context)
			else:
				message = "There is an issue with your registration. Please try again"
				
		except:
			message = "There is an issue with your registration. Please try again."
			messages.success(self.request, message)
			return HttpResponseRedirect(reverse('register_event'))


class GetName(TemplateView):

	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			results = []
			q = request.GET.get('term', '')
			table_name = request.GET.get('table', '')
			table = Table.objects.get(table_name=table_name)

			users = EventUsers.objects.filter(table = table)

			users = users.filter(first_name__icontains=q)

			for user in users:
				user_json = {}
				user_json['id'] = user.id
				user_json['label'] = user.first_name+ ' ' +user.last_name
				user_json['value'] = user.first_name+ ' ' +user.last_name
				results.append(user_json)

			data = json.dumps(results)

			mimetype = 'application/json'

			return HttpResponse(data , mimetype)

# def checkRegform(request):

# 	data  = {}
# 	if request.is_ajax():
# 		email = request.GET.get('email', '')

# 		users = RegisteredUsers.objects.filter(event_user__email=email)

# 		if len(users) > 0:
# 			data['success'] = "True"			
# 		else:
# 			data['message'] = "Email already exists. Please enter new mail !."
# 			data['success'] = "False"

# 		return HttpResponse(json.dumps(data), content_type='application/json')
# 	else:
# 		data['success'] = "False"	
# 	return HttpResponse(json.dumps(data), content_type='application/json')



class GetUserData(TemplateView):

    def get(self, request):
    	data = {}
    	django_messages = []
    	data['user_exist'] = ''
    	try:
    		username = request.GET['username']
    		selected_table = request.GET.get('selected_table', '')
    		new_table = request.GET.get('new_table', '')

    		if new_table:
    			table_other, created = Table.objects.create(table_name=new_table)
    			# data['other_table'] = 'Other'
    			data['success'] = "True"
    			return HttpResponse(json.dumps(data), content_type='application/json')

    		elif selected_table == 'Other':
    			tables = Table.objects.filter(table_name='Other')
    			if len(tables) == 1:
    				table = tables[0]
    		else:
    			table = Table.objects.get(table_name=selected_table)

    		name_list = username.split(' ', 1)
    		user = EventUsers.objects.get(first_name=name_list[0],last_name=name_list[1] )
    		# user = EventUsers.objects.get(first_name=username, table=table)

    		
    		# Checks user exist
    		try:
    			registered_user = RegisteredUsers.objects.get(event_user=user ,table=table)
    			data['balance'] = int(registered_user.balance_amount)
    			data['paid_amount'] = registered_user.amount_paid
    			data['user_exist'] = 'true'
    			print("User exist")
    		except:
    			print("user not exist")
    			data['user_exist'] = 'false'
    			data['other_table'] = ''

    		data['email'] = user.email
    		data['mobile'] = user.mobile
    		data['first_name'] = user.first_name
    		data['last_name'] = user.last_name    		
    		data['success'] = "True"
    		print("Data : ", data)

    		return HttpResponse(json.dumps(data), content_type='application/json')
    	except:
    		print("except from GetUserData")
    		data['success'] = "False"
    		data['error_msg'] = "something went WRONG"
    		return HttpResponse(json.dumps(data), content_type='application/json')

    	return HttpResponse(json.dumps(data), content_type='application/json')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

class ListUsers(TemplateView):
	template_name = 'user_list.html'

	def get(self, request, *args, **kwargs):
		context ={}
		registered_users = RegisteredUsers.objects.all()
		context['users'] = registered_users
		# user_list = []
		# for user in registered_users:
		# 	data = {}
		# 	data['name'] = user.event_user.first_name+' '+user.event_user.last_name
		# 	user_list.append(data)
		return render(request, self.template_name, context)

class InvoiceView(TemplateView):
	# template_name = 'invoice.html'
	template_name = 'coupon.html'
	def get(self, request, *args, **kwargs):
		context = {}
		pk = kwargs.pop('pk')
		event_reg = RegisteredUsers.objects.get(id=pk)
		context['event_register'] = event_reg
		return render(request, self.template_name, context)

