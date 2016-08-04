from django.contrib import admin

from hardware import models


@admin.register(models.GpioButton)
class GpioButtonAdmin(admin.ModelAdmin):
    list_display = ['action', 'bcm_pin']