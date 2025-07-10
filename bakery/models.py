from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from cart.models import Cart
from django.core.exceptions import ValidationError

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, default='none')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Topping(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    serves = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return self.name


class BakeryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='bakery_images/')
    available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    ingredients = models.TextField(blank=True)
    sales = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')

    def get_price_with_currency(self):
        return f"Kshs {self.price:.2f}"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def update_profile(self, address=None, phone_number=None):
        if address:
            self.address = address
        if phone_number:
            self.phone_number = phone_number
        self.save()


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    phone_number = models.CharField(max_length=15, blank=True, null=True) 
    address = models.CharField(max_length=255, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True) 

    def __str__(self):
        return f"Order #{self.id} by {self.user.username if self.user else 'Anonymous'}"

    def update_total_price(self):
        self.total_price = sum(item.total_price for item in self.order_items.all())
        self.save()

    def update_payment_status(self, status):
        if status in dict(self.PAYMENT_STATUS_CHOICES):
            self.payment_status = status
            self.save()

    class Meta:
        indexes = [
            models.Index(fields=['status', 'payment_status']),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(BakeryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)


class NewsletterSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('unsubscribed', 'Unsubscribed'),
    ]

    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active') 
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
