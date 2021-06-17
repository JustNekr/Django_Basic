from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import UpdateView, CreateView

from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserEditForm
from django.contrib import auth
from django.urls import reverse, reverse_lazy

from authapp.models import ShopUser


class MyLoginView(LoginView):
    authentication_form = ShopUserLoginForm
    template_name = 'authapp/login.html'
    extra_context = {'title': 'вход'}


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class UserRegisterView(CreateView):
    model = ShopUser
    form_class = ShopUserRegisterForm
    template_name = 'authapp/register.html'
    success_url = reverse_lazy('auth:login')
    extra_context = {'title': 'регистрация'}

    def send_verify_link(self):
        verify_link = reverse('auth:verify', args=[self.object.email, self.object.activation_key])
        subject = 'account verify'
        message = f'Verify link: \n{settings.DOMAIN_NAME}{verify_link}'
        return send_mail(subject, message, settings.EMAIL_HOST_USER, [self.object.email], fail_silently=False)

    def form_valid(self, form):
        user = super(UserRegisterView, self).form_valid(form)
        self.send_verify_link()
        return user


class UserUpdateView(UpdateView):
    model = ShopUser
    form_class = ShopUserEditForm
    template_name = 'authapp/edit.html'
    success_url = reverse_lazy('auth:edit')
    extra_context = {'title': 'редактирование'}

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form()
        for field_name, field in form.fields.items():
            if not field_name.startswith('is_'):
                field.widget.attrs['class'] = 'form-control'
        return form


def verify(request, email, key):
    user = ShopUser.objects.filter(email=email).first()
    if user and user.activation_key == key and not user.is_activation_key_expired():
        user.is_active = True
        user.activation_key = ''
        user.activation_key_created = None
        user.save()
        auth.login(request, user)
    return render(request, 'authapp/verify.html')