import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify


# validator function for salesman
def validate_salesman(pk):
    user = CustomUser.objects.get(pk=pk)
    if user.role == 1:
        return user
    else:
        raise ValidationError("This user is buyer, buyer cannot make lots")


# validator function for buyer
def validate_buyer(pk):
    user = CustomUser.objects.get(pk=pk)
    if user.role == 2:
        return user
    else:
        raise ValidationError("This user is salesman, salesman can't place orders")


class CustomUser(AbstractUser):
    SALESMAN = 1
    BUYER = 2

    ROLE_CHOICES = (
        (SALESMAN, 'Salesman'),
        (BUYER, 'Buyer'),
    )
    # Roles for separating users and restricting their rights
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    def get_salesman_url(self):
        if self.role == 1:
            return reverse('salesman-detail', kwargs={'username': self.username})
        return reverse('error-page')


class Flower(models.Model):
    WHITE = 1
    BLACK = 2
    BLUE = 3
    GREEN = 4

    name = models.CharField(
        max_length=120)
    LOAD_SHADE = (
        (WHITE, "White"),
        (BLACK, "Black"),
        (BLUE, "Blue"),
        (GREEN, "Green")
    )
    shade = models.PositiveSmallIntegerField(
        choices=LOAD_SHADE,
        blank=True,
        null=True,
        help_text="Select shade"
    )

    class META:
        ordering = ["name"]
        verbose_name = 'Flower'
        verbose_name_plural = 'Flowers'

    def __str__(self):
        return self.name


class Lot(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    salesman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        validators=[validate_salesman],
        related_name="salesman",
    )
    title = models.CharField(
        max_length=120)
    flower = models.ForeignKey(
        Flower,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        blank=True
    )
    amount = models.IntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(auto_now=True)
    hide = models.BooleanField(default=True)

    class META:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Lot, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # return reverse('lot-detail', kwargs={'uuid': self.id, 'slug': self.slug})
        pass

    def __str__(self):
        return self.title


class Order(models.Model):
    description = models.TextField(
        help_text="Order comment"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        validators=[validate_salesman],
        related_name="buyer",
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class META:
        ordering = ["-created"]

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_absolute_url(self):
        # return reverse('order-detail', kwargs={'pk': self.pk})
        pass

    def __str__(self):
        return f'Order {self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    lot = models.ForeignKey(
        Lot,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    amount = models.IntegerField()

    class META:
        ordering = ["-amount"]

    def get_coast(self):
        return self.amount * self.lot.unit_price

