from django.core.validators import MinValueValidator
from django.db import models

from decimal import Decimal


from restaurants.file_path import get_pdf_file_path


class RestaurantModel(models.Model):
    address = models.CharField(max_length=256)
    dishes = models.ManyToManyField("DishModel")


class PrinterModel(models.Model):
    name = models.CharField(max_length=64)
    serial_num = models.CharField(max_length=64, verbose_name="Serial Number")
    brand = models.CharField(max_length=64, null=True, blank=True)
    restaurant = models.ForeignKey(
        "RestaurantModel",
        on_delete=models.CASCADE,
        related_name="printers"
    )


class DishModel(models.Model):
    name = models.CharField(max_length=128)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )


class OrderModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    dishes = models.ManyToManyField(
        "DishModel",
        through="DishOrderModel",
    )
    restaurant = models.ForeignKey(
        "RestaurantModel",
        on_delete=models.CASCADE,
        related_name="receipts"
    )

    @property
    def total(self):
        return self.dishes.aggregate(total_price=models.Sum('price'))['total_price'] or 0


class DishOrderModel(models.Model):
    dish = models.ForeignKey(
        "DishModel",
        on_delete=models.CASCADE,
        related_name="dish_orders",
    )
    order = models.ForeignKey(
        "OrderModel",
        on_delete=models.CASCADE,
        related_name="order_dishes",
    )
    quantity = models.SmallIntegerField(default=1)

    @property
    def amount(self):
        return self.dish.price * self.quantity


class ReceiptModel(models.Model):
    TYPE_CHOICES = (
        (0, "client"),
        (1, "kitchen"),
    )
    STATUS_CHOICES = (
        (0, "Not Generated"),
        (1, "Generated"),
    )

    type = models.SmallIntegerField(
        choices=TYPE_CHOICES,
    )
    status = models.SmallIntegerField(
        choices=STATUS_CHOICES,
        default=0,
    )
    pdf_file = models.FileField(
        upload_to=get_pdf_file_path,
    )
    order = models.ForeignKey(
        "OrderModel",
        on_delete=models.CASCADE,
        related_name="receipts",
    )

    class Meta:
        unique_together = [("order", "type")]
