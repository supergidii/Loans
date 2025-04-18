from django.contrib import admin
from .models import Investor, Investment, Pairing

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_waiting', 'waiting_since', 'phone_number')
    list_filter = ('is_waiting',)
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('investor', 'amount', 'created_at', 'maturation_date', 'is_matured', 'paired')
    list_filter = ('is_matured', 'paired')
    search_fields = ('investor__user__username',)

@admin.register(Pairing)
class PairingAdmin(admin.ModelAdmin):
    list_display = ('investor', 'paired_investment', 'created_at')
    search_fields = ('investor__user__username', 'paired_investment__investor__user__username')
