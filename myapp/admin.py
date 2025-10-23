from django.contrib import admin
from .models import CustomUser,mapped
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(mapped)
