from django.contrib import admin

from restaurants.models import (
    RestaurantModel,
    PrinterModel,
    DishModel,
    OrderModel,
    ReceiptModel,
)

admin.site.register(RestaurantModel)
admin.site.register(PrinterModel)
admin.site.register(DishModel)
admin.site.register(OrderModel)
admin.site.register(ReceiptModel)
