from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, NewsletterSubscription, Category, Topping, Size

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number']

    email = forms.EmailField(required=True) 
    first_name = forms.CharField(max_length=30, required=True) 
    last_name = forms.CharField(max_length=30, required=True)  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        
        if self.cleaned_data.get('email'):
            user_profile.user.email = self.cleaned_data['email']
        if self.cleaned_data.get('first_name'):
            user_profile.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            user_profile.user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user_profile.user.save() 
            user_profile.save()  

        return user_profile
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ToppingForm(forms.ModelForm):
    class Meta:
        model = Topping
        fields = ['name', 'price_adjustment']


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name', 'price_adjustment', 'serves']