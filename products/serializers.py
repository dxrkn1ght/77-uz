from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "seller", "created_at"]
        read_only_fields = ["seller"]

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        return super().create(validated_data)
