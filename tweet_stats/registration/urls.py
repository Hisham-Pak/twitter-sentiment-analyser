from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/resend_mail/', views.resend_mail, name='resend_mail'),
    path('activate/<uidb64>/<token>/', views.Activate.as_view(), name='activate'),
]