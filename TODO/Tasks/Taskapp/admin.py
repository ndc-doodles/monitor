from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register(Register)


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ('date', 'session', 'point_text', 'status')
    list_filter = ('date', 'session', 'status')