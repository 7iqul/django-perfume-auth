from rest_framework import serializers
from .models import Perfume


class PerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = '__all__'   # id, name, brand, price, size_ml, description, in_stock