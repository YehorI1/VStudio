from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.contrib import messages





class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'email', 'password1', 'password2']:
            if field in self.fields:
                self.fields[field].help_text = ''
        if 'email' in self.fields:
            self.fields['email'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email


class AutorisIndexView(TemplateView):
    template_name = 'tut_autoris/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context




def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next") or "home"

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url)

        messages.error(request, "Неправильний логін або пароль.")

    return render(request, "auth/login.html", {
        "next": request.GET.get("next", "")
    })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    return redirect('home')

# def signin(request):
#     context = {}
#     return render(request, "auth/signin.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    return render(request, "auth/register.html", {
        "form": form,
        "title": "Регистрация"
    })





