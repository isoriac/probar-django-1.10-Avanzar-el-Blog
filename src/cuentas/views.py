from django.contrib.auth import(
	authenticate,
	get_user_model,
	login,
	logout
	)
from django.shortcuts import render

from .forms import UserLoginForm

# Create your views here.
def login_view(request):
	titulo = "Login"
	form = UserLoginForm(request.POST or None)
	if form.is_valid():
		usuario = form.cleaned_data.get("usuario")
		password = form.cleaned_data.get("password")
	return render(request, "form.html", {"form": form, "titulo": titulo})

def register_view(request):
	return render(request, "form.html", {})

def logout_view(request):
	return render(request, "form.html", {})