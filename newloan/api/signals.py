from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import Investment, Investor, Pairing

@receiver(post_save, sender=Investment)
def check_maturation(sender, instance, created, **kwargs):
    if not created and instance.maturation_date <= timezone.now() and not instance.is_matured:
        # Mark the investment as matured
        instance.is_matured = True
        instance.save()

        # Check for waiting investors with remaining amounts
        waiting_investors = Investor.objects.filter(is_waiting=True).order_by('created_at')
        
        for waiting_investor in waiting_investors:
            # Get the waiting investor's unpaired investment
            new_investment = Investment.objects.filter(
                investor=waiting_investor,
                remaining_amount__gt=0
            ).first()

            if new_investment and instance.remaining_amount > 0:
                # Determine the amount to pair
                amount_to_pair = min(new_investment.remaining_amount, instance.remaining_amount)

                # Create the pairing
                Pairing.objects.create(
                    investor=waiting_investor,
                    paired_investment=instance,
                    paired_amount=amount_to_pair
                )

                # Update remaining amounts
                new_investment.remaining_amount -= amount_to_pair
                instance.remaining_amount -= amount_to_pair

                # Save the changes
                new_investment.save()
                instance.save()

                # If the new investment is fully paired, remove waiting status
                if new_investment.remaining_amount == 0:
                    waiting_investor.is_waiting = False
                    waiting_investor.save()

                # If the matured investment is fully paired, mark it as paired
                if instance.remaining_amount == 0:
                    instance.paired = True
                    instance.save()
                    break  # Exit the loop as this matured investment is fully paired 