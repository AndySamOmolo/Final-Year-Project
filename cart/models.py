from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.CharField(max_length=40, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart (Session: {self.session})"

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_price()
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('bakery.BakeryItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    size = models.ForeignKey('bakery.Size', on_delete=models.SET_NULL, null=True, blank=True)
    custom_message = models.CharField(max_length=255, null=True, blank=True)
    toppings = models.ForeignKey('bakery.Topping', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.get_size_display()}) in {self.cart}"

    def get_total_price(self):
        return self.quantity * self.price
