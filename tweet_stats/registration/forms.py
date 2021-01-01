from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'email')    

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Make sure you\'ve entered correct password twice. Passwords don\'t match.')
        return cd['password2']
        
    def clean_email(self):
       cd = self.cleaned_data
       email = cd['email']
       if User.objects.filter(email=email):
            raise forms.ValidationError("Email exists, you must choose a different email.")
       return cd['email']


class EmailForm(forms.ModelForm):
    email=forms.EmailField(required=True, help_text="You must register with a valid email")

    class Meta:
        model = User
        fields=["email"]
    
    def clean_email(self):
        email=self.cleaned_data.get("email")
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already in use, please try with another account.")
        return email