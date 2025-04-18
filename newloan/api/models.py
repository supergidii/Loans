from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta
import uuid
from django.db.models import Sum

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional investor details
    created_at = models.DateTimeField(auto_now_add=True)
    is_waiting = models.BooleanField(default=False)  # Track if the investor is waiting
    waiting_since = models.DateTimeField(null=True, blank=True)  # Track when they started waiting
    waiting_investment_id = models.IntegerField(null=True, blank=True)  # Track which investment is waiting
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    referral_code = models.CharField(max_length=36, blank=True, null=True, db_index=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add available balance field

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    @property
    def has_invested(self):
        return self.investments.exists()

    def __str__(self):
        return self.user.username

class Investment(models.Model):
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    maturation_date = models.DateTimeField()
    is_matured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='available', choices=[
        ('available', 'Available'),
        ('matched', 'Matched'),
        ('sold', 'Sold'),
    ])
    is_for_sale = models.BooleanField(default=False)
    paired = models.BooleanField(default=False)
    pairing = models.ForeignKey('Pairing', on_delete=models.SET_NULL, null=True, blank=True, related_name='investments')
    
    def calculate_daily_interest(self):
        """Calculate the daily interest (1% of the investment amount)"""
        return self.amount * Decimal('0.01')
    
    def calculate_projected_interest(self):
        """Calculate the projected interest for the entire investment period"""
        days = (self.maturation_date - self.created_at).days
        return self.calculate_daily_interest() * days
    
    def calculate_end_return(self):
        """Calculate the total return (principal + interest) at maturity"""
        return self.amount + self.calculate_projected_interest()
    
    def __str__(self):
        return f"Investment of ${self.amount} by {self.investor.user.username}"

class Pairing(models.Model):
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='pairings')
    paired_investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='pairings')
    paired_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Pairing of ${self.paired_amount} for {self.investor.user.username}"

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_received')
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_investment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def add_investment(self, amount):
        """Add investment amount and calculate earnings"""
        self.total_investment_amount += amount
        # Calculate earnings (e.g., 5% of investment)
        earnings = amount * Decimal('0.05')
        self.total_earnings += earnings
        self.save()
        return earnings

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

class InvestmentSale(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='sales')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    
    def __str__(self):
        return f"Sale of {self.investment} by {self.seller.username} for ${self.price}"
