from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)   # unique email
    is_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=[("user", "User"), ("admin", "Admin")],
        default="user"
    )
    def __str__(self):
        return self.username
class mapped(models.Model):
    url=models.CharField(max_length=70)
    shorter_url=models.CharField(max_length=20)
    created_at=models.DateTimeField(auto_now=datetime)
    def __str__(self):
        return self.url
class Product(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    url= models.CharField(max_length=70)
    def __str__(self):
        return self.user.username
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()






    

