from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, EmailForm
from .tokens import account_activation_token
from django import forms

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.views.generic import View

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            request.session['username'] = user.username
            print(request.session)
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account on {}'.format(current_site.domain)
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/confirm_registration.html')
    else:
        form = UserRegistrationForm()
    return render(request, "registration/signup.html", {'form': form})

def resend_mail(request):
    print(request.session)
    username = request.session['username']
    user = User.objects.get(username=username)
    current_site = get_current_site(request)
    mail_subject = 'Please activate your account on {}'.format(current_site.domain)
    message = render_to_string('registration/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
                mail_subject, message, to=[to_email]
    )
    email.send()

    return render(request, 'registration/confirm_registration.html')

class Activate(View):
    def get(self, request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            print(uid)
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('main_app:dashboard')
        else:
            return HttpResponse('Activation link is invalid!')

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class=EmailForm
    success_url=reverse_lazy('main_app')
    template_name = 'registration/email_update_form.html'

    def get_object(self):
        return self.request.user
    
    def get_form(self, form_class=None):
        form = super(EmailUpdate,self).get_form()
        #modificar formulario en tiempo de ejecución
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2', 'placeholder' : 'e-mail'})
        form.fields['email'].label = ''
        form.fields['email'].help_text = ''
        return form