from django import forms

class UserLoginForm(forms.Form):
	usuario = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)