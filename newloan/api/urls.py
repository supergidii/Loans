from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-investment/', views.create_investment, name='create_investment'),
    path('match-investor/', views.match_investor, name='match_investor'),
    path('investment/<int:investment_id>/', views.investment_detail, name='investment_detail'),
    path('pairing/<int:pairing_id>/', views.pairing_detail, name='pairing_detail'),
    path('investment-status/', views.investment_status, name='investment_status'),
    path('investment-status/<int:investment_id>/', views.investment_status, name='investment_status_by_id'),
    path('cancel-waiting/', views.cancel_waiting, name='cancel_waiting'),
    path('confirm-payment/<int:pairing_id>/', views.confirm_payment, name='confirm_payment'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # Add new referral URLs
    path('referrals/', views.referrals, name='referrals'),
    path('referral-earnings/', views.referral_earnings, name='referral_earnings'),
    path('referral-code/', views.ReferralCodeView.as_view(), name='referral-code'),
    path('apply-referral/', views.ApplyReferralCodeView.as_view(), name='apply-referral'),
    path('waiting-to-be-paired/', views.waiting_to_be_paired, name='waiting_to_be_paired'),
    # Add Buy Shares URLs
    path('buy-shares/', views.buy_shares, name='buy_shares'),
    path('buy-share/<int:share_id>/', views.buy_share, name='buy_share'),
    # Add Sell Shares URLs
    path('sell-shares/', views.sell_shares, name='sell_shares'),
    path('sell-share/<int:share_id>/', views.sell_share, name='sell_share'),
    # Add API endpoints for selling and canceling investments
    path('investments/sell/', views.SellInvestmentView.as_view(), name='sell_investment_api'),
    path('investments/sell/<int:sale_id>/cancel/', views.CancelSaleView.as_view(), name='cancel_sale_api'),
] 