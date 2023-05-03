from django.contrib import admin
from .models import User, Event,MainEvent, EventRegister,TeamMates, ForgotPassword,PremimumTicket,Category, Transaction, Merch

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields=["name", "regno", "email", "phoneno"]
    list_display = ['name', 'regno', 'email', 'year', "phoneno"]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields=["name"]
    list_display = ['name', 'category', 'pay']
    list_filter = ("day",)

@admin.register(MainEvent)
class MainEventAdmin(admin.ModelAdmin):
    search_fields=["email"]
    list_display = ['email', 'day1', 'day2', 'day3']


admin.site.register(EventRegister)
admin.site.register(TeamMates)
admin.site.register(ForgotPassword)
admin.site.register(PremimumTicket)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Merch)