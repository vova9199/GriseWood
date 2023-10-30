from django.contrib import admin

# Register your models here.
from .models import Order, RawMaterial, CuttingRecord

admin.site.register(Order)
admin.site.register(RawMaterial)
admin.site.register(CuttingRecord)