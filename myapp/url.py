from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name='home'),
    path('signin',views.signin, name='login'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('signup/',views.signup, name='signup'),  # no '/' needed
    path('logout/',views.logout_view,name='logout'),
    path('api/<str:code>/', views.transfer, name='transfer'),
]
