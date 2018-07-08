# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, View

from events.models import (BookedHotel, Event, EventUsers, Hotel, OtpModel,
                           RegisteredUsers, RoomType)
from events.utils import send_otp

from .forms import (HotelDetailForm, OtpPostForm, PaymentDetailsForm,
                    ProfileInformationForm, ResetPasswordForm, TableSelectForm,
                    UserLoginForm, UserSignupForm)
from .mixins import RegisteredObjectMixin


class UserSignupView(FormView):
    template_name = 'user_registration/user_signup.html'
    form_class = UserSignupForm
    success_url = reverse_lazy('otp_post')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        try:
            event_user = EventUsers.objects.get(email=self.request.POST.get('email'),
                                                mobile=self.request.POST.get('mobile'))
            if not event_user.password:
                send_otp(event_user)
                return HttpResponseRedirect(self.success_url)
        except EventUsers.DoesNotExist:
            pass
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        user, created = EventUsers.objects.get_or_create(email=obj.email, mobile=obj.mobile)
        if created:
            user.is_active = False
            user.save()
            send_otp(user)

        return super(UserSignupView, self).form_valid(form)


class OtpPostView(FormView):
    template_name = 'user_registration/otp_post.html'
    form_class = OtpPostForm
    success_url = reverse_lazy('set_password')

    def post(self, request):
        otp = request.POST.get('otp')
        try:
            otp_obj = OtpModel.objects.get(otp=otp)
            event_user = EventUsers.objects.get(mobile=otp_obj.mobile)
            request.session['user'] = event_user.id
            if (datetime.now() - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return HttpResponse(json.dumps({'status': False, 'message': 'Otp Is Expired'}))
        except OtpModel.DoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'message': 'Invalid Otp'}))
        return HttpResponse(json.dumps({'status': True}))


class SetPassWordView(FormView):
    template_name = 'user_registration/otp_post.html'
    form_class = OtpPostForm
    success_url = reverse_lazy('user_login')

    def form_valid(self, form):
        user_id = self.request.session.get('user', None)
        if user_id is not None:
            user = EventUsers.objects.get(id=user_id)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = True
            user.save()
        data = {
            'status': True,
            'url': self.success_url
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse(form.errors)


class UserLoginView(FormView):
    template_name = 'user_registration/user_login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('event_register')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        context = {}
        if user:
            if user.is_active:
                login(self.request, user)
                if self.request.user.registered_obj and self.request.user.registered_obj.is_payment_completed:
                    return HttpResponseRedirect(reverse_lazy('user_profile'))
                else:
                    return HttpResponseRedirect(self.success_url)

            else:
                context['form'] = form
                context['error'] = 'Inactive'
                return render(self.request, self.template_name, context)
        else:
            context['form'] = form
            context['error'] = 'Invalid credentials'
            return render(self.request, self.template_name, context)


class UserTableRegistrationView(RegisteredObjectMixin, FormView):
    template_name = 'user_registration/event_register.html'
    form_class = TableSelectForm

    # success_url =

    def get_context_data(self, **kwargs):
        context = super(UserTableRegistrationView, self).get_context_data(**kwargs)
        context['table_form'] = TableSelectForm(instance=self.request.user)
        context['personal_info_form'] = ProfileInformationForm(instance=self.request.user)
        if self.request.user.registered_obj:
            context['personal_info_form'] = ProfileInformationForm(instance=self.request.user)
            context['payment_form'] = PaymentDetailsForm(instance=self.request.user.registered_obj)
            context['payement_details'] = RegisteredUsers.objects.get(id=self.request.user.registered_obj.id)
            if self.request.user.registered_obj.hotel_user:
                context['hotel_details_form'] = HotelDetailForm(instance=self.request.user.registered_obj.hotel_user)
            else:
                context['hotel_details_form'] = HotelDetailForm()
        else:
            # context['personal_info_form'] = ProfileInformationForm()
            context['payment_form'] = PaymentDetailsForm()
            context['hotel_details_form'] = HotelDetailForm()

        return context

    def form_valid(self, form):
        user_id = self.request.user.id
        table = form.cleaned_data['table']
        member_type = form.cleaned_data['member_type']
        if user_id:
            try:
                event_user = EventUsers.objects.get(id=user_id)
                event_user.member_type = member_type
                event_user.table = table
                event_user.save()
            except:
                pass

        data = {
            'message': "Successfully submitted Table data."
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse(form.errors)


class ProfileRegistrationView(RegisteredObjectMixin, TemplateView):
    template_name = 'user_registration/event_register.html'
    form_class = ProfileInformationForm

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email', '')
        first_name = self.request.POST.get('first_name', '')
        last_name = self.request.POST.get('last_name', '')
        mobile = self.request.POST.get('mobile', '')
        registration_type = self.request.POST.get('registration_type')
        amount_paid = self.request.POST.get('amount_paid')
        t_shirt_size = self.request.POST.get('t_shirt_size', '')
        form = ProfileInformationForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                event_user = EventUsers.objects.get(id=self.request.user.id)
                event_user.first_name = first_name
                event_user.last_name = last_name
                event_user.mobile = mobile
                event_user.email = email
                event_user.save()
                event = Event.objects.filter()[0]
                try:
                    registered_user = RegisteredUsers.objects.get(event_user=event_user, event=event)
                    registered_user.table = event_user.table
                    registered_user.save()

                except RegisteredUsers.DoesNotExist:
                    registered_user = RegisteredUsers.objects.create(event_user=event_user, event=event,
                                                                     table=event_user.table)

                if not registered_user.qrcode:
                    try:
                        registered_user.qrcode = RegisteredUsers.objects.latest('qrcode').qrcode
                        if not registered_user.qrcode.split('QRT')[1].startswith('8'):
                            registered_user.qrcode = 'QRT8001'
                        else:
                            qrcode_updated = registered_user.qrcode[-3:]
                            qrcode_updated_increment = int(qrcode_updated) + 1
                            qrcode_updated_length = len(str(qrcode_updated_increment))
                            if qrcode_updated_length == 1:
                                registered_user.qrcode = str('QRT8') + '00' + str(qrcode_updated_increment)
                            if qrcode_updated_length == 2:
                                registered_user.qrcode = str('QRT8') + '0' + str(qrcode_updated_increment)
                            else:
                                registered_user.qrcode = str('QRT8') + str(qrcode_updated_increment)
                    except:
                        registered_user.qrcode = 'QRT8001'
                registered_user.amount_paid = amount_paid
                registered_user.event_status = registration_type
                registered_user.t_shirt_size = t_shirt_size

                registered_user.save()
                data = {
                    'status': True,
                    'message': "Successfully submitted Table data."
                }
            except EventUsers.DoesNotExist:
                data = {
                    'status': False,
                    'message': "Something Went Wrong."
                }
        else:
            if 'email' in form.errors:
                del form.errors['email']
            data = form.errors
            if not data:
                data.update({'status': True})

        return JsonResponse(data)


class AjaxHotelRentCalculation(View):

    def get(self, request, *args, **kwargs):
        hotel = request.GET.get('hotel', '')
        room_type = request.GET.get('room_type')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        total_rent = 0
        if hotel and room_type:
            try:
                hotel_obj = Hotel.objects.get(id=hotel)
                room_rent = RoomType.objects.get(id=room_type, hotel=hotel_obj).net_rate
                if check_in and check_out:
                    no_of_days = int(check_out) - int(check_in)
                    total_rent = no_of_days * room_rent
                    data = {'total_rent': total_rent}
                    return JsonResponse(data)
            except Hotel.DoesNotExist:
                pass
        return JsonResponse({'total_rent': total_rent})


class HotelRegistrationView(RegisteredObjectMixin, FormView):
    template_name = 'user_registration/event_register.html'
    form_class = HotelDetailForm

    def form_invalid(self, form):
        html = render_to_string('user_registration/ajax_coupon.html', {"request": self.request})
        return HttpResponse(html)

    def form_valid(self, form):
        hotel = form.cleaned_data['hotel']
        room_type = form.cleaned_data['room_type']
        checkin_date = form.cleaned_data['checkin_date']
        checkout_date = form.cleaned_data['checkout_date']
        tottal_rent = form.cleaned_data['tottal_rent']
        if hotel and room_type:
            registered_user = RegisteredUsers.objects.get(event_user=self.request.user.id)
            try:
                hotel_user = BookedHotel.objects.get(registered_users=registered_user)
                hotel_user.hotel = hotel
            except BookedHotel.DoesNotExist:
                hotel_user = BookedHotel.objects.create(registered_users=registered_user, hotel=hotel)
            hotel_user.room_type = room_type
            hotel_user.tottal_rent = tottal_rent
            hotel_user.checkin_date = checkin_date
            hotel_user.checkout_date = checkout_date
            hotel_user.room_type.rooms_available -= 1
            hotel_user.room_type.save()
            hotel_user.save()
        html = render_to_string('user_registration/ajax_coupon.html', {"request": self.request})
        return HttpResponse(html)


class PaymentRegistrationView(RegisteredObjectMixin, FormView):
    template_name = 'user_registration/event_register.html'
    form_class = PaymentDetailsForm
    success_url = reverse_lazy('coupon_success')

    def form_valid(self, form):

        payment = form.cleaned_data['payment']
        reciept_number = form.cleaned_data['reciept_number']
        reciept_file = form.cleaned_data['reciept_file']
        if payment:
            try:
                user_payment = RegisteredUsers.objects.get(event_user=self.request.user.id)
                user_payment.payment = payment
                user_payment.reciept_number = reciept_number
                user_payment.reciept_file = reciept_file
                user_payment.is_payment_completed = True
                user_payment.save()
            except RegisteredUsers.DoesNotExist:
                pass
        return JsonResponse({'status': True, 'url': self.success_url})

    def form_invalid(self, form):
        return JsonResponse(form.errors)


class CouponSuccessView(TemplateView):
    template_name = 'user_registration/coupon_success.html'

    def get_context_data(self, **kwargs):
        context = super(CouponSuccessView, self).get_context_data(**kwargs)
        context['payement_details'] = RegisteredUsers.objects.get(id=self.request.user.registered_obj.id)
        return context


class UserProfileView(TemplateView):
    model = RegisteredUsers
    template_name = 'user_registration/profile.html'


class ResetPassword(FormView):
    form_class = ResetPasswordForm
    template_name = 'user_registration/forgot_password.html'
    success_url = reverse_lazy('otp_post')

    def post(self, request, *args, **kwargs):
        mobile = request.POST.get('mobile')
        try:
            user = EventUsers.objects.get(mobile=mobile)
            send_otp(user)
            return JsonResponse({'status': True, 'url': self.success_url})
        except EventUsers.DoesNotExist:
            return HttpResponse(json.dumps({'status': False, 'message': 'Number DoesNot Exist'}))
