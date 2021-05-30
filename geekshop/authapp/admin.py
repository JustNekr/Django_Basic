from django.contrib import admin
from .models import ShopUser
from basketapp.models import Basket

admin.site.register(ShopUser)
admin.site.register(Basket)