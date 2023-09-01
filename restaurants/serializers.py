from rest_framework import serializers

from restaurants.models import (
    DishModel,
    RestaurantModel,
    PrinterModel,
    DishOrderModel,
    OrderModel,
    ReceiptModel,
)


class DishModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishModel
        fields = "__all__"


class PrinterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterModel
        fields = "__all__"


class PrinterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterModel
        fields = ("name",)


class RestaurantModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantModel
        fields = ("id", "address", "dishes")
        read_only_fields = ("id",)


class RestaurantRetrieveSerializer(RestaurantModelSerializer):
    dishes = DishModelSerializer(many=True)


class RestaurantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantModel
        fields = (
            "id",
            "address",
        )


class DishOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishOrderModel
        fields = ("dish", "quantity")


class ReceiptModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptModel
        fields = ("id", "type", "status", "created_at")


class ReceiptRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptModel
        fields = ("id", "created", "type", "status", "pdf_file", "order")


class OrderModelSerializer(serializers.ModelSerializer):
    dishes = DishOrderSerializer(many=True, source="order_dishes")

    class Meta:
        model = OrderModel
        fields = "__all__"
        read_only_fields = ("id", "created_at",)

    def create(self, validated_data):
        dish_order_data = validated_data.pop("order_dishes", [])

        order = OrderModel.objects.create(**validated_data)

        dishes = [
            DishOrderModel(order=order, **dr_data)
            for dr_data in dish_order_data
        ]

        DishOrderModel.objects.bulk_create(dishes)

        return order


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderModel
        fields = ("id", "created_at", "total")


class OrderRetrieveSerializer(serializers.ModelSerializer):
    restaurant = RestaurantAddressSerializer()
    dishes = DishModelSerializer(many=True)
    receipts = ReceiptModelSerializer(many=True)

    class Meta:
        model = OrderModel
        fields = (
            "id",
            "total",
            "dishes",
            "created_at",
            "restaurant",
            "receipts",
        )
