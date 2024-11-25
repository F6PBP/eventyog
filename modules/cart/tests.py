from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from modules.main.models import (
    UserProfile, Event, Merchandise, EventCart, MerchCart, TicketPrice
)
from django.urls import reverse

class CartTests(TestCase):

    def setUp(self):
        self.client = Client()  # Create a client instance
        # Create user and profile
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = UserProfile.objects.create(user=self.user, wallet=Decimal("100000.00"))

        # Create event and ticket
        self.event = Event.objects.create(
            title="Test Event",
            description="Test event description",
            start_time="2024-01-01T10:00:00Z",
            end_time="2024-01-01T12:00:00Z",
        )
        self.ticket_price = TicketPrice.objects.create(event=self.event, name="Standard", price=Decimal("25000.00"))

        # Create merchandise
        self.merch = Merchandise.objects.create(
            image_url="https://example.com/image.png",
            name="Test Merch",
            description="Test description",
            price=Decimal("15000.00")
        )

        # Create EventCart and MerchCart items
        self.event_cart = EventCart.objects.create(user=self.user, ticket=self.ticket_price, quantity=2)
        self.merch_cart = MerchCart.objects.create(user=self.user, merchandise=self.merch, quantity=3)

    def test_profile_wallet_initialization(self):
        """Test if user profile wallet initializes with correct default balance."""
        self.client.force_login(self.user)  # Ensure user is logged in
        self.assertEqual(self.profile.wallet, Decimal("100000.00"))

    def test_total_price_event_cart(self):
        """Test if the total price calculation in EventCart is correct."""
        self.client.force_login(self.user)  # Ensure user is logged in
        total_price = self.event_cart.totalPrice()
        self.assertEqual(total_price, Decimal("50000.00"))

    def test_total_price_merch_cart(self):
        """Test if the total price calculation in MerchCart is correct."""
        self.client.force_login(self.user)  # Ensure user is logged in
        total_price = self.merch_cart.totalPrice()
        self.assertEqual(total_price, Decimal("45000.00"))
    
    def test_view_cart_initial_balance(self):
        """Test if the initial balance appears correctly in the cart view."""
        self.client.force_login(self.user)  # Ensure user is logged in
        
        # Print the user's wallet balance for debugging
        # print(f"User Wallet Balance: {self.profile.wallet}")

        response = self.client.get(reverse("cart:main"))
        
        # Check the response content for debugging
        # print(response.content)

        self.assertContains(response, '<span id="wallet-balance">100000.00</span>')

    def test_cart_total_price_calculation(self):
        """Test if the cumulative total price in cart is correctly calculated."""
        self.client.force_login(self.user)  # Ensure user is logged in
        response = self.client.get(reverse("cart:main"))
        self.assertContains(response, '<span id="total-price">95000.00</span>')

    def test_checkout_sufficient_balance(self):
        """Test checkout with sufficient balance in wallet."""
        self.client.force_login(self.user)  # Ensure user is logged in
        response = self.client.post(reverse("cart:checkout"), {
            'event': {self.event_cart.id: {'quantity': 2, 'pricePerItem': 25000}},
            'merch': {self.merch_cart.id: {'quantity': 3, 'pricePerItem': 15000}}
        }, content_type="application/json")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(self.profile.wallet, Decimal("5000.00"))

    def test_checkout_insufficient_balance(self):
        """Test checkout with insufficient wallet balance."""
        self.client.force_login(self.user)  # Ensure user is logged in
        self.profile.wallet = Decimal("20000.00")
        self.profile.save()

        response = self.client.post(reverse("cart:checkout"), {
            'event': {self.event_cart.id: {'quantity': 2, 'pricePerItem': 25000.00}},
            'merch': {self.merch_cart.id: {'quantity': 3, 'pricePerItem': 15000.00}}
        }, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Insufficient wallet balance.')

    def test_cart_quantity_update(self):
        """Test if updating the cart quantity adjusts prices and remaining balance."""
        self.client.force_login(self.user)  # Ensure user is logged in
        self.event_cart.quantity = 1
        self.event_cart.save()
        
        response = self.client.get(reverse("cart:main"))
        self.assertContains(response, '<span id="total-price">70000.00</span>')

    def test_add_event_to_cart(self):
        """Test if adding an event ticket to the cart is reflected correctly."""
        self.client.force_login(self.user)  # Ensure user is logged in
        new_event_cart = EventCart.objects.create(user=self.user, ticket=self.ticket_price, quantity=1)
        response = self.client.get(reverse("cart:main"))
        self.assertContains(response, '<span id="total-price">120000.00</span>')  # 95000 + 25000

    def test_add_merch_to_cart(self):
        """Test if adding merchandise to the cart updates correctly in the view."""
        self.client.force_login(self.user)  # Ensure user is logged in
        new_merch = Merchandise.objects.create(
            image_url="https://example.com/new_image.png",
            name="New Merch",
            description="New description",
            price=Decimal("20000.00")
        )
        new_merch_cart = MerchCart.objects.create(user=self.user, merchandise=new_merch, quantity=2)
        
        response = self.client.get(reverse("cart:main"))
        self.assertContains(response, '<span id="total-price">135000.00</span>')  # 95000 + (20000*2)