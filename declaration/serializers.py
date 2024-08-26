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
    name = serializers.SerializerMethodField()
    number_of_packages = serializers.SerializerMethodField()
    detail = serializers.SerializerMethodField()


    class Meta:
        model = Declaration
        fields = ["id","created_at","declaration_date","name","declaration_no","net_weight",
                  "gross_weight","measurements","number_of_packages","regime_type","cargo_type","declaration_type","cargo_channel",
                  "transaction_type","trade_type","detail"]
    


    def get_detail (self, obj):
        return obj.declaration_no
    
    def get_number_of_packages (self, obj):
        return obj.nmbr_of_packages
    
    def get_name(self, obj):
        return obj.request_no
    
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
    
class DelcarationListSerilaizer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    detail = serializers.SerializerMethodField()
    detail1 = serializers.SerializerMethodField()
    detail2 = serializers.SerializerMethodField()
    detail3 = serializers.SerializerMethodField()

    class Meta:
        model = Declaration
        fields = ["id","name","detail","detail1","detail2","detail3"]


    def get_name(self, obj):
        return obj.request_no
    
    def get_detail (self, obj):
        return obj.declaration_no
    

    def get_detail1 (self, obj):
        return obj.net_weight
    
    def get_detail2 (self, obj):
        return obj.measurements
    
    def get_detail3 (self, obj):
        return obj.created_at    
    


class UpdateDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ["is_verified","updated_by_id"]

class ListDeclarationLogSerializer(serializers.ModelSerializer):
    declaration = DeclarationSerializer()
    class Meta:
        model = Declaration_log
        fields = ["status","comment","declaration","id","created_at","updated_at","is_deleted"]