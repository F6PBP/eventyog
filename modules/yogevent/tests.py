from django.test import TestCase
from modules.main.models import Event, TicketPrice, Rating, EventCart
from django.contrib.auth.models import User

class EventTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Concert",
            description="A live music concert",
            date="2024-12-31",
            location="Music Hall",
            tickets_available=100
        )

    def test_create_event(self):
        self.assertEqual(self.event.title, "Concert")
        self.assertEqual(self.event.tickets_available, 100)

    def test_edit_event(self):
        self.event.title = "Rock Concert"
        self.event.description = "A live rock music concert"
        self.event.save()
        updated_event = Event.objects.get(id=self.event.id)
        self.assertEqual(updated_event.title, "Rock Concert")
        self.assertEqual(updated_event.description, "A live rock music concert")

    def test_delete_event(self):
        event_id = self.event.id
        self.event.delete()
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(id=event_id)

class TicketPriceTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Concert",
            description="A live music concert",
            date="2024-12-31",
            location="Music Hall",
            tickets_available=100
        )
        self.user = User.objects.create_user(username="johndoe", password="password")
        self.ticket_price = TicketPrice.objects.create(event=self.event, price=50.00)

    def test_set_ticket_price(self):
        self.assertEqual(self.ticket_price.event, self.event)
        self.assertEqual(self.ticket_price.price, 50.00)

    def test_edit_ticket_price(self):
        self.ticket_price.price = 60.00
        self.ticket_price.save()
        updated_ticket_price = TicketPrice.objects.get(id=self.ticket_price.id)
        self.assertEqual(updated_ticket_price.price, 60.00)

    def test_buy_ticket(self):
        # Simulate ticket purchase
        tickets_before = self.event.tickets_available
        self.event.tickets_available -= 1
        self.event.save()
        tickets_after = self.event.tickets_available
        self.assertEqual(tickets_after, tickets_before - 1)

class RatingTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Concert",
            description="A live music concert",
            date="2024-12-31",
            location="Music Hall",
            tickets_available=100
        )
        self.user = User.objects.create_user(username="johndoe", password="password")

    def test_add_rating(self):
        rating = Rating.objects.create(
            event=self.event,
            user=self.user,
            score=5,
            comment="Amazing event!"
        )
        self.assertEqual(rating.event, self.event)
        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.comment, "Amazing event!")

    def test_update_rating(self):
        rating = Rating.objects.create(
            event=self.event,
            user=self.user,
            score=5,
            comment="Amazing event!"
        )
        rating.score = 4
        rating.comment = "Good event, but could be better."
        rating.save()
        updated_rating = Rating.objects.get(id=rating.id)
        self.assertEqual(updated_rating.score, 4)
        self.assertEqual(updated_rating.comment, "Good event, but could be better.")

class EventCartTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Concert",
            description="A live music concert",
            date="2024-12-31",
            location="Music Hall",
            tickets_available=100
        )
        self.user = User.objects.create_user(username="johndoe", password="password")

    def test_add_to_cart(self):
        cart = EventCart.objects.create(user=self.user)
        cart.events.add(self.event)
        self.assertIn(self.event, cart.events.all())
