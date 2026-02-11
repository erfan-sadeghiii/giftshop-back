from django.db import models
from django.conf import settings

from django.db import models
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories"
    )

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=100)            # e.g. "Color", "RAM"
    is_general = models.BooleanField(default=False)    # True if global, like "Brand"

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(unique=False, blank=True, null=True)

    description = models.TextField()
    price = models.BigIntegerField()
    stock_quantity = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return self.price - (self.price * (self.discount / 100))


class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_features"
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="feature_values"
    )
    value = models.CharField(max_length=200)  # e.g. "Red", "16GB"

    def __str__(self):
        return f"{self.product.title} - {self.feature.name}: {self.value}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images"  , null=True,
        blank=True)
    image = models.ImageField(upload_to="products/"  ,null=True,blank=True)

    def __str__(self):
        return f"Image for {self.product.title}"


class Cart(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
        ('paid', 'Paid'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user.username} ({self.status})"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"










from django.db import models
from django.conf import settings   # <-- important


class Comment(models.Model):
    product = models.ForeignKey(
        "shop.Product",   # adjust app label if Product is in shop app
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # now points to your custom User model
        on_delete=models.CASCADE,
        related_name="comments"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    isLiked = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"









class Slider(models.Model):
    picture = models.ImageField(upload_to='sliders/')
    link = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Slider {self.id}"





class Banner(models.Model):
    POSITION_CHOICES = (
        ('left', 'Left'),
        ('right', 'Right'),
    )
    
    position = models.CharField(max_length=5, choices=POSITION_CHOICES)
    image = models.ImageField(upload_to='banners/')
    link = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Delete existing banner with the same position before saving new one
        Banner.objects.filter(position=self.position).exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.position} banner"








class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    user = models.ForeignKey(  settings.AUTH_USER_MODEL,   # now points to your custom User model
        on_delete=models.CASCADE,
        related_name="tickets"
    )
   
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='tickets/files/', blank=True, null=True)
    dateTime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"{self.title} ({self.status})"


class Reply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(  settings.AUTH_USER_MODEL,   # now points to your custom User model
        on_delete=models.CASCADE,
        related_name="replies"
    )
    content = models.TextField()
    dateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.ticket.title}"









# models.py
from django.db import models

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    link = models.CharField(max_length=255, default="/products")
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class MenuSection(models.Model):
    menuCategory = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.menuCategory.name} - {self.title}"


class MenuItem(models.Model):
    section = models.ForeignKey(MenuSection, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=255, default="/products")
    query = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name

class AmazingSlider(models.Model):
    products = models.ManyToManyField(Product, related_name="amazing_sliders")
    duration = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']










# payments/models.py


class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    authority = models.CharField(max_length=255, unique=True)
    amount = models.PositiveIntegerField()
    items = models.JSONField(default=list)
    # Payment result fields
    is_paid = models.BooleanField(default=False)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    card_pan = models.CharField(max_length=50, null=True, blank=True)
    card_hash = models.CharField(max_length=255, null=True, blank=True)
    fee_type = models.CharField(max_length=50, null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)

    # Errors
    error_code = models.IntegerField(null=True, blank=True)
    error_message = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    offer_code = models.CharField(max_length=50,null=True, blank=True)
    def __str__(self):
        return f"{self.user} - {self.amount} - {self.authority}-is paid :{self.is_paid}"






from django.utils import timezone

class Discount(models.Model):
    PERCENT = 'percent'
    FIXED = 'fixed'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENT, 'Percent'),
        (FIXED, 'Fixed'),
    ]

    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    value = models.PositiveIntegerField()

    max_usage = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    min_order_price = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)


    offer_code = models.CharField(max_length=50, null=True, blank=True)
    discount_amount = models.IntegerField(default=0)

    def is_valid_time(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at

    def __str__(self):
        return self.code




class DiscountUsage(models.Model):
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    order_id = models.PositiveIntegerField()
    used_at = models.DateTimeField(auto_now_add=True)
    # is_used = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['discount', 'user'],
                name='unique_discount_per_user'
            )
        ]
