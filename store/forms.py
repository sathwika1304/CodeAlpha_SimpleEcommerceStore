from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full name")
    phone = forms.CharField(max_length=20, label="Phone number")
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Delivery address")
    payment_method = forms.ChoiceField(choices=[("cod", "Cash on Delivery")], label="Payment method")

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if len(phone) < 7 or len(phone) > 20:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone
