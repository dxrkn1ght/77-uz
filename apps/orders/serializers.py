from rest_framework import serializers
from .models import Order, OrderItem
from apps.catalog.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "buyer", "status", "created_at", "items"]
        read_only_fields = ["buyer", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(buyer=self.context["request"].user, **validated_data)
        for item in items_data:
            product = Product.objects.get(pk=item["product"].id if hasattr(item["product"], "id") else item["product"])
            OrderItem.objects.create(order=order, product=product, quantity=item["quantity"], price=item.get("price", product.price))
        return order
