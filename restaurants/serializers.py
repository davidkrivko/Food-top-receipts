from rest_framework import serializers

from restaurants.models import (
    DishModel,
    RestaurantModel,
    PrinterModel,
    DishOrderModel,
    OrderModel,
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
        fields = ("id", "type", "status", "total")


class OrderRetrieveSerializer(serializers.ModelSerializer):
    restaurant = RestaurantAddressSerializer()

    class Meta:
        model = OrderModel
        fields = (
            "id",
            "dishes",
            "total",
            "created_at",
            "restaurant",
            "receipts",
        )
