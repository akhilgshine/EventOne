from django import forms
from django.contrib.auth.forms import UserCreationForm

from events.models import (MEMBER_CHOICES, PAYMENT_CHOICES, STATUS_CHOICES,
                           T_SHIRT_CHOICES, BookedHotel, EventUsers, Hotel,
                           RegisteredUsers, RoomType, Table)

from .validators import validate_phone


class UserSignupForm(forms.ModelForm):
    email = forms.EmailField()
    mobile = forms.CharField(validators=[validate_phone])

    class Meta:
        model = EventUsers
        fields = ['email', 'mobile']

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['email'].widget.attrs.update({'autofocus': 'autofocus'})
        self.fields['mobile'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['mobile'].widget.attrs['placeholder'] = 'Mobile'
        self.fields['mobile'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean(self):
        cleaned_data = super(UserSignupForm, self).clean()
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        if EventUsers.objects.filter(mobile=mobile).exists():
            self.add_error('mobile', 'This mobile number is already registered')


class OtpPostForm(UserCreationForm):
    class Meta:
        model = EventUsers
        fields = ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(OtpPostForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['email'].widget.attrs.update({'autofocus': 'autofocus'})
        self.fields['password'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class TableSelectForm(forms.ModelForm):
    table = forms.ModelChoiceField(queryset=Table.objects.all())
    member_type = forms.ChoiceField(choices=MEMBER_CHOICES)

    class Meta:
        model = EventUsers
        fields = ['table', 'member_type']

    def __init__(self, *args, **kwargs):
        super(TableSelectForm, self).__init__(*args, **kwargs)
        self.fields['table'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['table'].widget.attrs['placeholder'] = 'Select Table'
        self.fields['table'].widget.attrs.update({'autofocus': 'autofocus'})
        self.fields['member_type'].widget.attrs['class'] = 'form-control common-input form-group'


class ProfileInformationForm(forms.ModelForm):
    registration_type = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.RadioSelect())
    t_shirt_size = forms.ChoiceField(choices=T_SHIRT_CHOICES, required=False)

    amount_paid = forms.CharField()

    class Meta:
        model = EventUsers
        fields = ['first_name', 'last_name', 'mobile', 'email', 'registration_type', 'amount_paid', 't_shirt_size']

    def __init__(self, *args, **kwargs):
        super(ProfileInformationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['mobile'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['mobile'].widget.attrs['placeholder'] = 'Enter Mobile'
        self.fields['email'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['email'].widget.attrs['readonly'] = 'True'
        self.fields['mobile'].widget.attrs['readonly'] = 'True'
        self.fields['t_shirt_size'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['amount_paid'].widget.attrs['class'] = 'form-control common-input form-group m'
        self.fields['amount_paid'].widget.attrs['placeholder'] = 'Registration Fee'
        if self.instance and self.instance.member_type == 'Tabler':
            self.fields['registration_type'].choices = [(u'Couple', u'Couple'), (u'Stag', u'Stag')]
        if self.instance.registered_obj:
            self.fields['registration_type'].initial = self.instance.registered_obj.event_status
            self.fields['amount_paid'].initial = self.instance.registered_obj.amount_paid
            self.fields['t_shirt_size'].initial = self.instance.registered_obj.t_shirt_size

    def clean(self):
        cleaned_data = super(ProfileInformationForm, self).clean()
        if 'email' in self._errors:
            del self._errors['email']
        return cleaned_data


class HotelDetailForm(forms.ModelForm):
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all(), required=False)
    room_type = forms.ModelChoiceField(queryset=RoomType.objects.all(), required=False)
    checkin_date = forms.DateTimeField(input_formats=["%d/%m/%y"])
    checkout_date = forms.DateTimeField(input_formats=["%d/%m/%y"])

    class Meta:
        model = BookedHotel
        fields = ['hotel', 'tottal_rent', 'checkin_date', 'checkout_date', 'room_type']

    def __init__(self, *args, **kwargs):
        super(HotelDetailForm, self).__init__(*args, **kwargs)
        self.fields['hotel'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['tottal_rent'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['checkin_date'].widget.attrs['class'] = 'form-control common-input form-group datepicker'
        self.fields['checkin_date'].widget.attrs['placeholder'] = 'Check In'
        self.fields['checkout_date'].widget.attrs['class'] = 'form-control common-input form-group datepicker'
        self.fields['room_type'].widget.attrs['class'] = 'hidden'
        self.fields['checkout_date'].widget.attrs['placeholder'] = 'Check Out'


class PaymentDetailsForm(forms.ModelForm):
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect())

    class Meta:
        model = RegisteredUsers
        fields = ['payment', 'reciept_number', 'reciept_file']

    def __init__(self, *args, **kwargs):
        super(PaymentDetailsForm, self).__init__(*args, **kwargs)
        self.fields['reciept_number'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['reciept_file'].widget.attrs['class'] = 'form-control common-input form-group'


class ResetPasswordForm(forms.Form):
    mobile = forms.CharField(validators=[validate_phone], required=True)

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['mobile'].widget.attrs['class'] = 'form-control common-input b0'
        self.fields['mobile'].widget.attrs['placeholder'] = 'Enter Registered Number'
        self.fields['mobile'].widget.attrs.update({'autofocus': 'autofocus'})


class PartialAmountDuePaymentForm(forms.Form):
    amount = forms.CharField(max_length=255)
    receipt_number = forms.CharField()
    receipt_file = forms.ImageField()
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super(PartialAmountDuePaymentForm, self).__init__(*args, **kwargs)
        self.fields['receipt_number'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['amount'].widget.attrs['class'] = 'form-control common-input form-group'
        self.fields['receipt_file'].widget.attrs['class'] = 'form-control common-input form-group'
