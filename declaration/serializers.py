from rest_framework import serializers
from .models import *

class RegimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegimeType
        fields = '__all__'

class TradeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeType
        fields = '__all__'

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'

class CargoChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoChannel
        fields = '__all__'

class DeclarationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeclarationType
        fields = '__all__'

class CargoTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoType
        fields = '__all__'

class DeclarationSerializer(serializers.ModelSerializer):
    regime_type = RegimeTypeSerializer()
    cargo_type = CargoTypeSerializer()
    declaration_type = DeclarationTypeSerializer()
    cargo_channel = CargoChannelSerializer()
    transaction_type = TransactionTypeSerializer()
    trade_type = TradeTypeSerializer()

    class Meta:
        model = Declaration
        fields = ["id","created_at","updated_at","is_deleted","declaration_date","request_no","declaration_no","net_weight",
                  "gross_weight","measurements","nmbr_of_packages","regime_type","cargo_type","declaration_type","cargo_channel",
                  "transaction_type","trade_type","is_verified"]

class UpdateDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ["is_verified"]