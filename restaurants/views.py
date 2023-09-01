from rest_framework import viewsets, mixins, status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response

from restaurants.models import (
    DishModel,
    RestaurantModel,
    PrinterModel,
    OrderModel,
)
from restaurants.permissions import IsReadOnlyOrStaff
from restaurants.serializers import (
    DishModelSerializer,
    RestaurantAddressSerializer,
    RestaurantModelSerializer,
    RestaurantRetrieveSerializer,
    PrinterModelSerializer,
    OrderListSerializer,
    OrderModelSerializer,
    OrderRetrieveSerializer,
)
from restaurants.tasks import generate_receipts_for_order


class DishModelViewSet(viewsets.ModelViewSet):
    serializer_class = DishModelSerializer
    queryset = DishModel.objects.all()
    permission_classes = [IsReadOnlyOrStaff]


class PrinterModelViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = PrinterModel.objects.all()
    serializer_class = PrinterModelSerializer
    permission_classes = [IsAdminUser]


class RestaurantModelViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = RestaurantModel.objects.all()
    permission_classes = [IsReadOnlyOrStaff]

    def get_serializer_class(self):
        if self.action == "list":
            return RestaurantAddressSerializer
        elif self.action == "retrieve":
            return RestaurantRetrieveSerializer
        return RestaurantModelSerializer


class OrderModelViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Create action make two types of
    orders at the same time,
    everything else default
    """
    permission_classes = [IsAuthenticated]

    queryset = OrderModel.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        order_id = serializer.instance.id
        generate_receipts_for_order.delay(order_id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
