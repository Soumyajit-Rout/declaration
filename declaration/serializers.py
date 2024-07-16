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
    regime_type = serializers.SerializerMethodField()
    cargo_type = serializers.SerializerMethodField()
    declaration_type = serializers.SerializerMethodField()
    cargo_channel = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()
    trade_type = serializers.SerializerMethodField()

    class Meta:
        model = Declaration
        fields = ["id","created_at","updated_at","is_deleted","declaration_date","request_no","declaration_no","net_weight",
                  "gross_weight","measurements","nmbr_of_packages","regime_type","cargo_type","declaration_type","cargo_channel",
                  "transaction_type","trade_type","is_verified"]
    
    def get_regime_type(self, obj):
        return obj.regime_type.name
    
    def get_cargo_type(self, obj):
        return obj.cargo_type.name
    
    def get_declaration_type(self, obj):
        return obj.declaration_type.name
    
    def get_cargo_channel(self, obj):
        return obj.cargo_channel.name
    
    def get_transaction_type(self, obj):
        return obj.transaction_type.name
    
    def get_trade_type(self, obj):
        return obj.trade_type.name
    
class UpdateDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ["is_verified"]

class ListDeclarationLogSerializer(serializers.ModelSerializer):
    declaration = DeclarationSerializer()
    class Meta:
        model = Declaration_log
        fields = ["status","comment","declaration","id","created_at","updated_at","is_deleted"]