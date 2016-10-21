from django import forms

from django.contrib.auth import(
	authenticate,
	get_user_model,
	login,
	logout
	)

User = get_user_model()

class UserLoginForm(forms.Form):
	usuario = forms.CharField(label="Usuario o email")
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self, *args, **kwargs):
		usuario = self.cleaned_data.get("usuario")
		password = self.cleaned_data.get("password")

		if usuario and password:
			user_qs1 = User.objects.filter(username__iexact=usuario)
			user_qs2 = User.objects.filter(email__iexact=usuario)
			user_qs = (user_qs1|user_qs2).distinct()
			if not user_qs.exists() and user_qs.count() != 1:
				raise forms.ValidationError("Ese usuario no existe")
			else:
				user = user_qs.first()
				if not user.check_password(password):
					raise forms.ValidationError("Password incorrecto")
				if not user.is_active:
					raise forms.ValidationError("Info invalida")

		return super(UserLoginForm, self).clean(*args, **kwargs)