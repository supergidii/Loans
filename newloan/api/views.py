from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from decimal import Decimal
from django.db.models import Sum, F, Q, Count
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import random
import string
import json
from django.http import JsonResponse

from .forms import InvestorProfileForm
from .models import Investor, Investment, Pairing, Referral, InvestmentSale
from .tasks import match_waiting_investors

def index(request):
    return render(request, 'index.html')

# Create your views here.

@login_required
def create_investment(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        maturation_date = request.POST['maturation_date']
        investor = request.user.investor
        
        investment = Investment.objects.create(
            investor=investor, 
            amount=amount, 
            maturation_date=maturation_date
        )
        return redirect('api:investment_detail', investment_id=investment.id)
    
    return render(request, 'create_investment.html')

@login_required
def match_investor(request):
    new_investor = request.user.investor
    matured_investments = Investment.objects.filter(is_matured=True, remaining_amount__gt=0).order_by('created_at')

    if matured_investments.exists():
        # Get the new investment that needs pairing
        new_investment = Investment.objects.filter(
            investor=new_investor,
            remaining_amount__gt=0
        ).first()

        if new_investment:
            for matured_investment in matured_investments:
                if new_investment.remaining_amount <= 0:
                    break  # If new investment is fully paired, exit the loop

                # Calculate the return amount for the matured investment
                return_amount = matured_investment.calculate_end_return()
                
                # Determine the amount to pair - use the return amount
                amount_to_pair = min(new_investment.remaining_amount, return_amount)

                # Create the pairing
                Pairing.objects.create(
                    investor=new_investor,
                    paired_investment=matured_investment,
                    paired_amount=amount_to_pair
                )

                # Update remaining amounts
                new_investment.remaining_amount -= amount_to_pair
                matured_investment.remaining_amount = 0  # Set to 0 since we're using the full return amount

                # Update paired status if fully paired
                if matured_investment.remaining_amount == 0:
                    matured_investment.paired = True
                
                # Save the changes
                new_investment.save()
                matured_investment.save()

                messages.success(request, f"Your investment has been paired with {matured_investment.investor.user.username} for ${amount_to_pair}")

            # If the investment still has remaining amount, add to waiting queue
            if new_investment.remaining_amount > 0:
                new_investor.is_waiting = True
                new_investor.waiting_since = timezone.now()
                new_investor.save()
                messages.info(request, f"Your remaining investment of ${new_investment.remaining_amount} has been added to the waiting queue.")
            
            return redirect('api:investment_status')
    
    # If no matured investments are available or no new investment to pair
    new_investor.is_waiting = True
    new_investor.waiting_since = timezone.now()
    new_investor.save()
    messages.info(request, "You have been added to the waiting queue. You will be paired when investments mature.")
    return render(request, 'waiting_for_pairing.html', {
        'investor': new_investor
    })

@login_required
def investment_detail(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, investor=request.user.investor)
    return render(request, 'investment_detail.html', {'investment': investment})

@login_required
def pairing_detail(request, pairing_id):
    pairing = get_object_or_404(Pairing, id=pairing_id)
    return render(request, 'pairing_detail.html', {'pairing': pairing})

@login_required
def investment_status(request, investment_id=None):
    # Get the investment
    if investment_id:
        investment = get_object_or_404(Investment, id=investment_id, investor=request.user.investor)
    else:
        # Get the most recent investment for the current user
        investment = Investment.objects.filter(
            investor=request.user.investor,
        ).order_by('-created_at').first()

    # Check if the investment has matured
    if investment and investment.maturation_date <= timezone.now() and not investment.is_matured:
        investment.is_matured = True
        investment.save()  # This will trigger the pairing process

    # Get all pairings for this investment
    pairings = None
    if investment:
        pairings = Pairing.objects.filter(
            investor=request.user.investor,
            paired_investment__created_at__lte=investment.created_at
        ).order_by('-created_at')

    return render(request, 'investment_status.html', {
        'investment': investment,
        'pairings': pairings,
    })

@login_required
def sell_shares(request):
    """
    View for selling shares.
    """
    # Get all investments for the current user that are not for sale
    available_investments = Investment.objects.filter(
        investor=request.user.investor,
        status='matched',
        is_for_sale=False
    ).select_related('pairing', 'pairing__paired_investment', 'pairing__paired_investment__investor', 'pairing__paired_investment__investor__user').order_by('-created_at')
    
    # Get all investments that are already for sale
    listed_sales = InvestmentSale.objects.filter(
        seller=request.user,
        status='pending'
    ).select_related('investment', 'investment__pairing', 'investment__pairing__paired_investment', 'investment__pairing__paired_investment__investor', 'investment__pairing__paired_investment__investor__user').order_by('-created_at')
    
    # Check if any investments have matured to determine if we should show the phone column
    show_phone_column = False
    for investment in available_investments:
        if investment.is_matured and investment.paired:
            show_phone_column = True
            break
    
    for sale in listed_sales:
        if sale.investment.is_matured and sale.investment.paired:
            show_phone_column = True
            break
    
    context = {
        'available_investments': available_investments,
        'listed_sales': listed_sales,
        'show_phone_column': show_phone_column,
    }
    
    return render(request, 'sell_shares.html', context)

@login_required
def dashboard(request):
    investor = request.user.investor
    # Only show investments that have been paired and confirmed
    investments = Investment.objects.filter(
        investor=investor,
        pairing__confirmed=True
    ).distinct().order_by('-created_at')

    # Calculate returns for each investment
    total_returns = sum(inv.calculate_end_return() for inv in investments)
    total_interest = sum(inv.calculate_projected_interest() for inv in investments)
    projected_returns = sum(inv.calculate_end_return() for inv in investments if not inv.is_matured)

    # Calculate waiting amount as cumulative total returns
    waiting_returns = sum(
        inv.calculate_end_return() 
        for inv in investments 
        if inv.remaining_amount > 0
    )

    # Calculate statistics
    stats = investments.aggregate(
        total_invested=Sum('amount'),
        total_paired=Sum('amount') - Sum('remaining_amount'),
        active_investments=Count('id')
    )

    # Check if there are matured investments available for pairing
    matured_investments_available = Investment.objects.filter(
        is_matured=True, 
        remaining_amount__gt=0
    ).exclude(
        investor=investor
    ).exists()

    # Get active pairings for the user
    active_pairings = Pairing.objects.filter(
        investor=investor,
        confirmed=True
    ).select_related(
        'paired_investment', 
        'paired_investment__investor', 
        'paired_investment__investor__user'
    ).order_by('-created_at')

    # Get the investment the user is waiting with (if any)
    waiting_investment = None
    if investor.is_waiting and hasattr(investor, 'waiting_investment_id'):
        waiting_investment = Investment.objects.filter(id=investor.waiting_investment_id).first()

    context = {
        'investments': investments,
        'total_invested': stats['total_invested'] or Decimal('0.00'),
        'total_paired': stats['total_paired'] or Decimal('0.00'),
        'total_waiting': waiting_returns,  # Using cumulative returns instead of remaining amount
        'active_investments': stats['active_investments'] or 0,
        'total_returns': total_returns,
        'total_interest': total_interest,
        'projected_returns': projected_returns,
        'matured_investments_available': matured_investments_available,
        'active_pairings': active_pairings,
        'waiting_investment': waiting_investment
    }

    return render(request, 'dashboard.html', context)

@login_required
def update_profile(request):
    investor = request.user.investor
    
    # Check if profile has already been updated
    if investor.phone_number and investor.referral_code:
        messages.info(request, 'Your profile has already been updated.')
        return redirect('api:dashboard')
    
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST, instance=investor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('api:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InvestorProfileForm(instance=investor)
    
    return render(request, 'update_profile.html', {'form': form})

@login_required
def cancel_waiting(request):
    if request.method == 'POST':
        investor = request.user.investor
        investment_id = request.POST.get('investment_id')

        if investment_id:
            investment = get_object_or_404(Investment, id=investment_id, investor=investor)
            
            # Only cancel if the investment has remaining amount and investor is waiting
            if investment.remaining_amount > 0 and investor.is_waiting:
                investor.is_waiting = False
                investor.save()
                messages.success(request, "Your waiting status has been cancelled.")
            else:
                messages.error(request, "Unable to cancel waiting status.")
        
        return redirect('api:dashboard')
    
    return redirect('api:dashboard')

@login_required
def confirm_payment(request, pairing_id):
    pairing = get_object_or_404(Pairing, id=pairing_id)

    # Check if the user confirming is the owner of the paired matured investment
    if request.user != pairing.paired_investment.investor.user:
        messages.error(request, "You are not authorized to confirm this payment.")
        return redirect('api:investment_status')

    # Confirm the payment and start the countdown for the new investor's investment
    pairing.confirmed = True
    pairing.paired_investment.is_matured = False  # Mark as paid
    pairing.save()

    # Start countdown for the new investor's investment (by setting a maturation date)
    new_investment = Investment.objects.filter(
        investor=pairing.investor,
        remaining_amount__gt=0
    ).first()
    
    if new_investment:
        # Set the maturation date based on your business logic (e.g., 30 days)
        new_investment.maturation_date = timezone.now() + timezone.timedelta(days=30)
        new_investment.save()
        
        # Notify the new investor
        messages.success(
            request, 
            f"Payment confirmed. The new investor's countdown has started and will mature in 30 days."
        )
    else:
        messages.warning(request, "Payment confirmed but no active investment found for the new investor.")

    return redirect('api:investment_status')

# Authentication views
def register_view(request):
    referral_code = request.GET.get('ref')
    referred_by = None
    
    if referral_code:
        try:
            referred_by = Investor.objects.get(referral_code=referral_code)
        except Investor.DoesNotExist:
            messages.warning(request, "Invalid referral code provided.")
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Check if username already exists
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    messages.error(request, "Username already exists. Please choose a different username.")
                    return render(request, 'register.html', {'form': form})
                
                # Check if passwords match
                if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'register.html', {'form': form})
                
                # Create user
                user = form.save()
                
                # Create investor record
                investor = Investor.objects.create(user=user, referred_by=referred_by)
                
                # Create referral record if applicable
                if referred_by:
                    Referral.objects.create(
                        referrer=referred_by.user,  # Use the User instance, not the Investor
                        referred_user=user,
                        code=referral_code
                    )
                    messages.success(request, f"Registration successful! You were referred by {referred_by.user.username}.")
                else:
                    messages.success(request, "Registration successful! Welcome to the Investment Platform.")
                
                # Log the user in
                login(request, user)
                return redirect('api:dashboard')
                
            except Exception as e:
                messages.error(request, f"An error occurred during registration: {str(e)}")
                return render(request, 'register.html', {'form': form})
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('api:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('api:login')

@login_required
def referrals(request):
    try:
        # Get referrals where the current user is the referrer
        referrals = Referral.objects.filter(
            referrer=request.user,
            is_active=True
        ).select_related('referred_user')
        
        # Calculate total earnings
        total_earnings = sum(referral.total_earnings for referral in referrals)
        
        context = {
            'referrals': referrals,
            'total_earnings': total_earnings,
            'total_referrals': referrals.count()
        }
        return render(request, 'referrals.html', context)
    except Exception as e:
        messages.error(request, f"Error loading referrals: {str(e)}")
        return redirect('api:dashboard')

@login_required
def referral_earnings(request):
    try:
        # Get referrals where the current user is the referrer
        referrals = Referral.objects.filter(
            referrer=request.user,
            is_active=True
        ).select_related('referred_user')
        
        # Calculate total earnings
        total_earnings = sum(referral.total_earnings for referral in referrals)
        
        context = {
            'referrals': referrals,
            'total_earnings': total_earnings,
            'total_referrals': referrals.count()
        }
        return render(request, 'referral_earnings.html', context)
    except Exception as e:
        messages.error(request, f"Error loading referral earnings: {str(e)}")
        return redirect('api:dashboard')

class InvestmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(request.data.get('amount', 0))
            if amount <= 0:
                return Response({'error': 'Investment amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

            investor = Investor.objects.get(user=request.user)
            
            # Create the investment
            investment = Investment.objects.create(
                investor=investor,
                amount=amount
            )

            # Check if user was referred
            try:
                referral = Referral.objects.get(referred_user=request.user)
                # Add the investment amount to referral tracking
                referral.add_investment(amount)
            except Referral.DoesNotExist:
                pass

            # Trigger matching process
            from .tasks import match_waiting_investors
            match_waiting_investors.delay()

            return Response({
                'message': 'Investment created successfully',
                'investment_id': investment.id,
                'amount': str(investment.amount),
                'created_at': investment.created_at
            }, status=status.HTTP_201_CREATED)

        except Investor.DoesNotExist:
            return Response({'error': 'Investor profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get or create referral code for the user
            referral, created = Referral.objects.get_or_create(
                referrer=request.user,
                defaults={'code': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}
            )
            
            return Response({
                'referral_code': referral.code,
                'total_earnings': str(referral.total_earnings),
                'total_investments': str(referral.total_investment_amount)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ApplyReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            code = request.data.get('code')
            if not code:
                return Response({'error': 'Referral code is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user already has a referral
            if Referral.objects.filter(referred_user=request.user).exists():
                return Response({'error': 'You already have a referral'}, status=status.HTTP_400_BAD_REQUEST)

            # Find the referral code
            try:
                referral = Referral.objects.get(code=code, is_active=True)
                if referral.referrer == request.user:
                    return Response({'error': 'Cannot use your own referral code'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create new referral record
                Referral.objects.create(
                    referrer=referral.referrer,
                    referred_user=request.user,
                    code=code
                )
                
                return Response({'message': 'Referral code applied successfully'})
            except Referral.DoesNotExist:
                return Response({'error': 'Invalid referral code'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def waiting_to_be_paired(request):
    # Get all unpaired investments for the current user
    unpaired_investments = Investment.objects.filter(
        investor=request.user.investor,
        paired=False,
        is_matured=False
    ).order_by('-created_at')
    
    # Get all pairings that need confirmation
    pending_pairings = Pairing.objects.filter(
        paired_investment__investor=request.user.investor,
        confirmed=False
    ).select_related('investor', 'paired_investment')
    
    context = {
        'unpaired_investments': unpaired_investments,
        'pending_pairings': pending_pairings,
    }
    return render(request, 'waiting_to_be_paired.html', context)

@login_required
def buy_shares(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount'))
            days = int(data.get('days', 30))  # Default to 30 days if not specified
            
            if amount <= 0:
                return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
            if days < 1:
                return JsonResponse({'error': 'Days must be at least 1'}, status=400)
            
            # Get the investor
            investor = request.user.investor
            
            # Calculate maturation date based on days
            from django.utils import timezone
            from datetime import timedelta
            maturation_date = timezone.now() + timedelta(days=days)
            
            # Create the investment
            investment = Investment.objects.create(
                investor=investor,
                amount=amount,
                remaining_amount=amount,
                maturation_date=maturation_date,
                status='matched'  # Set status to matched since it's immediately available for sale
            )
            
            # Automatically create a sale listing for the investment
            sale = InvestmentSale.objects.create(
                investment=investment,
                seller=request.user,
                price=amount  # Set initial price to the investment amount
            )
            
            return JsonResponse({
                'message': 'Investment bid placed successfully',
                'investment_id': investment.id,
                'sale_id': sale.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in buy_shares: {error_details}")
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    # GET request - show the form
    investor = request.user.investor
    return render(request, 'buy_shares.html', {'available_balance': investor.available_balance})

@login_required
def buy_share(request, share_id):
    """
    View for buying a specific share.
    """
    # Get the share
    share = get_object_or_404(Investment, id=share_id, status='available', is_for_sale=True)
    
    if request.method == 'POST':
        # Get the amount to buy
        amount = Decimal(request.POST.get('amount', 0))
        
        # Validate the amount
        if amount <= 0 or amount > share.amount:
            messages.error(request, 'Invalid amount to buy.')
            return redirect('api:buy_shares')
        
        # Check if the user has enough balance
        if request.user.investor.available_balance < amount:
            messages.error(request, 'You do not have enough balance to buy this share.')
            return redirect('api:buy_shares')
        
        # Create a new investment for the buyer
        buyer_investment = Investment.objects.create(
            investor=request.user.investor,
            amount=amount,
            maturation_date=share.maturation_date,
            status='matched',
            matched_at=timezone.now()
        )
        
        # Update the seller's investment
        share.amount -= amount
        if share.amount == 0:
            share.status = 'sold'
        share.save()
        
        # Transfer the money from buyer to seller
        buyer = request.user.investor
        seller = share.investor
        
        buyer.available_balance -= amount
        buyer.total_invested += amount
        buyer.save()
        
        seller.available_balance += amount
        seller.save()
        
        messages.success(request, f'You have successfully bought a share for ${amount}.')
        return redirect('api:investment_detail', investment_id=buyer_investment.id)
    
    return redirect('api:buy_shares')

@login_required
def sell_share(request, share_id):
    """
    View for selling a specific share.
    """
    # Get the investment
    investment = get_object_or_404(Investment, id=share_id, investor=request.user.investor, is_for_sale=False)
    
    if request.method == 'POST':
        # Get the amount to sell
        amount = Decimal(request.POST.get('amount', 0))
        
        # Validate the amount
        if amount <= 0 or amount > investment.amount:
            messages.error(request, 'Invalid amount to sell.')
            return redirect('api:sell_shares')
        
        # Mark the investment as for sale
        investment.is_for_sale = True
        investment.status = 'available'
        investment.save()
        
        messages.success(request, f'You have successfully listed your investment for sale for ${amount}.')
        return redirect('api:sell_shares')
    
    return redirect('api:sell_shares')

class SellInvestmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            investment_id = request.data.get('investment_id')
            price = Decimal(request.data.get('price', 0))
            
            if not investment_id or price <= 0:
                return Response({
                    'success': False,
                    'message': 'Invalid investment ID or price'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the investment
            investment = get_object_or_404(Investment, id=investment_id, investor=request.user.investor)
            
            # Check if investment is already for sale
            if InvestmentSale.objects.filter(investment=investment, status='pending').exists():
                return Response({
                    'success': False,
                    'message': 'This investment is already listed for sale'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the sale listing
            sale = InvestmentSale.objects.create(
                investment=investment,
                seller=request.user,
                price=price
            )
            
            # Update investment status
            investment.is_for_sale = True
            investment.status = 'available'
            investment.save()
            
            return Response({
                'success': True,
                'message': 'Investment listed for sale successfully',
                'sale_id': sale.id
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CancelSaleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, sale_id):
        try:
            # Get the sale
            sale = get_object_or_404(InvestmentSale, id=sale_id, seller=request.user, status='pending')
            
            # Update sale status
            sale.status = 'cancelled'
            sale.save()
            
            # Update investment status
            investment = sale.investment
            investment.is_for_sale = False
            investment.status = 'matched'
            investment.save()
            
            return Response({
                'success': True,
                'message': 'Sale listing cancelled successfully'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
