from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Investor, Investment, Pairing, Referral, User
from django.db.models import Q
from django.db import transaction

@shared_task
def match_waiting_investors():
    """
    Match matured investments with waiting investors.
    A matured investment can be paired with an immature investment from another user.
    """
    # Get all matured investments that haven't been fully paired
    matured_investments = Investment.objects.filter(
        is_matured=True,
        remaining_amount__gt=0
    ).select_related('investor')

    for matured_inv in matured_investments:
        # Find immature investments from other users
        immature_investments = Investment.objects.filter(
            is_matured=False,
            remaining_amount__gt=0
        ).exclude(
            investor=matured_inv.investor  # Exclude investments from the same user
        ).select_related('investor')

        for immature_inv in immature_investments:
            # Calculate how much can be paired
            pairing_amount = min(matured_inv.remaining_amount, immature_inv.remaining_amount)
            
            if pairing_amount > 0:
                # Create the pairing
                pairing = Pairing.objects.create(
                    investor=immature_inv.investor,
                    paired_investment=matured_inv,
                    paired_amount=pairing_amount,
                    paired_to=matured_inv.investor  # Set the paired_to field to the matured investment's investor
                )

                # Update remaining amounts
                matured_inv.remaining_amount -= pairing_amount
                immature_inv.remaining_amount -= pairing_amount

                # Update paired status if fully paired
                if matured_inv.remaining_amount == 0:
                    matured_inv.paired = True
                if immature_inv.remaining_amount == 0:
                    immature_inv.paired = True
                    # Update investor's waiting status
                    immature_inv.investor.is_waiting = False
                    immature_inv.investor.waiting_since = None
                    immature_inv.investor.waiting_investment_id = None
                    immature_inv.investor.save()

                # Save the changes
                matured_inv.save()
                immature_inv.save()

                # If the matured investment is fully paired, break the loop
                if matured_inv.remaining_amount == 0:
                    break

def notify_user_of_pairing(investor, paired_investment, amount):
    subject = 'Investment Paired'
    message = f'Dear {investor.user.username},\n\nYour investment has been paired with {paired_investment.investor.user.username} for an amount of ${amount}.\n\nBest regards,\nLoan Management System'
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [investor.user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email to {investor.user.email}: {str(e)}")

@shared_task
def process_investment_matching():
    """
    Process investment matching for waiting investors.
    This task runs every minute to match waiting investors with available investments.
    """
    try:
        with transaction.atomic():
            # Get all waiting investors
            waiting_investors = User.objects.filter(
                investorprofile__status='waiting',
                investorprofile__is_active=True
            ).select_related('investorprofile')

            for investor in waiting_investors:
                # Get available investments that match the investor's criteria
                available_investments = Investment.objects.filter(
                    status='available',
                    amount__lte=investor.investorprofile.available_balance
                ).order_by('created_at')

                for investment in available_investments:
                    # Match the investment with the investor
                    investment.investor = investor
                    investment.status = 'matched'
                    investment.matched_at = timezone.now()
                    investment.save()

                    # Update investor profile
                    profile = investor.investorprofile
                    profile.available_balance -= investment.amount
                    profile.total_invested += investment.amount
                    profile.status = 'invested'
                    profile.save()

                    # Break if investor's balance is depleted
                    if profile.available_balance <= 0:
                        break

    except Exception as e:
        print(f"Error in process_investment_matching: {str(e)}")
        raise

@shared_task
def process_referral_earnings():
    """
    Process referral earnings for all active referrals.
    This task runs every 5 minutes to calculate and update referral earnings.
    """
    try:
        with transaction.atomic():
            # Get all active referrals
            active_referrals = Referral.objects.filter(
                is_active=True
            ).select_related('referrer', 'referred_user')

            for referral in active_referrals:
                # Get all investments made by the referred user
                investments = Investment.objects.filter(
                    investor=referral.referred_user,
                    status='matched',
                    created_at__gte=referral.created_at
                )

                # Calculate total investment amount
                total_investment = sum(investment.amount for investment in investments)
                
                # Update referral with new investment amount and earnings
                if total_investment > referral.total_investment_amount:
                    new_investment = total_investment - referral.total_investment_amount
                    referral.add_investment(new_investment)
                    referral.save()

    except Exception as e:
        print(f"Error in process_referral_earnings: {str(e)}")
        raise 