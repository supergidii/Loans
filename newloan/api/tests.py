from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Investor, Investment, Pairing
from .tasks import match_waiting_investors

class PairingTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
        # Create investors
        self.investor1 = Investor.objects.create(user=self.user1)
        self.investor2 = Investor.objects.create(user=self.user2)
        
        # Create a matured investment for user1
        self.matured_investment = Investment.objects.create(
            investor=self.investor1,
            amount=Decimal('1000.00'),
            remaining_amount=Decimal('1000.00'),
            maturation_date=timezone.now() - timedelta(days=1),  # Matured yesterday
            is_matured=True
        )
        
        # Create an immature investment for user2
        self.immature_investment = Investment.objects.create(
            investor=self.investor2,
            amount=Decimal('800.00'),
            remaining_amount=Decimal('800.00'),
            maturation_date=timezone.now() + timedelta(days=30),  # Matures in 30 days
            is_matured=False
        )

    def test_automatic_pairing(self):
        # Run the pairing task
        match_waiting_investors()
        
        # Check if a pairing was created
        pairing = Pairing.objects.first()
        self.assertIsNotNone(pairing, "No pairing was created")
        
        # Verify pairing details
        self.assertEqual(pairing.investor, self.investor2, "Wrong investor in pairing")
        self.assertEqual(pairing.paired_investment, self.matured_investment, "Wrong paired investment")
        self.assertEqual(pairing.paired_to, self.investor1, "Wrong paired_to investor")
        self.assertEqual(pairing.paired_amount, Decimal('800.00'), "Wrong paired amount")
        
        # Refresh investments from database
        self.matured_investment.refresh_from_db()
        self.immature_investment.refresh_from_db()
        
        # Check remaining amounts
        self.assertEqual(self.matured_investment.remaining_amount, Decimal('200.00'), 
                        "Matured investment remaining amount incorrect")
        self.assertEqual(self.immature_investment.remaining_amount, Decimal('0.00'), 
                        "Immature investment remaining amount incorrect")
        
        # Check paired status
        self.assertTrue(self.immature_investment.paired, "Immature investment not marked as paired")
        self.assertFalse(self.matured_investment.paired, "Matured investment incorrectly marked as paired")

    def test_multiple_pairings(self):
        # Create another immature investment for user2
        second_immature = Investment.objects.create(
            investor=self.investor2,
            amount=Decimal('300.00'),
            remaining_amount=Decimal('300.00'),
            maturation_date=timezone.now() + timedelta(days=30),
            is_matured=False
        )
        
        # Run the pairing task
        match_waiting_investors()
        
        # Check if both pairings were created
        pairings = Pairing.objects.all()
        self.assertEqual(pairings.count(), 2, "Wrong number of pairings created")
        
        # Verify the matured investment is now fully paired
        self.matured_investment.refresh_from_db()
        self.assertEqual(self.matured_investment.remaining_amount, Decimal('0.00'), 
                        "Matured investment should be fully paired")
        self.assertTrue(self.matured_investment.paired, "Matured investment should be marked as paired")

    def test_same_user_pairing_prevention(self):
        # Create another immature investment for user1 (same user as matured investment)
        same_user_investment = Investment.objects.create(
            investor=self.investor1,
            amount=Decimal('500.00'),
            remaining_amount=Decimal('500.00'),
            maturation_date=timezone.now() + timedelta(days=30),
            is_matured=False
        )
        
        # Run the pairing task
        match_waiting_investors()
        
        # Verify that the same user's investment was not paired
        same_user_investment.refresh_from_db()
        self.assertEqual(same_user_investment.remaining_amount, Decimal('500.00'),
                        "Same user's investment should not be paired")
        self.assertFalse(same_user_investment.paired,
                        "Same user's investment should not be marked as paired")
        
        # Verify that no pairing was created for the same user's investment
        same_user_pairing = Pairing.objects.filter(
            paired_investment=self.matured_investment,
            investor=self.investor1
        ).first()
        self.assertIsNone(same_user_pairing,
                         "Pairing should not be created between investments from the same user")
        
        # Verify that the original immature investment from different user was paired
        self.immature_investment.refresh_from_db()
        different_user_pairing = Pairing.objects.filter(
            paired_investment=self.matured_investment,
            investor=self.investor2
        ).first()
        self.assertIsNotNone(different_user_pairing,
                            "Pairing should be created for investments from different users")
