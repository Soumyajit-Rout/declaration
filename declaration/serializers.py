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


class DocumentSerializer(serializers.ModelSerializer):
    class Meta :
        model = Document
        fields = ["file"]
        
class ItemSerializer(serializers.ModelSerializer):
    hs_code = serializers.SerializerMethodField() 
    documents =  serializers.SerializerMethodField()

    class Meta:
        model = Items
        fields = ["id", "goods_description", "static_quantity_unit", "supp_quantity_unit", "unit_weight", 
                  "goods_value", "cif_value", "duty_fee", "hs_code","documents"]

    def get_hs_code(self, obj):
        return obj.hs_code.hs_code if obj.hs_code else None 
    
    def get_documents(self, obj):
        document = Document.objects.filter(item=obj)
        return DocumentSerializer(document, many=True).data

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
    assign_user_id = serializers.SerializerMethodField()
    assign_user_name = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()


    class Meta:
        model = Declaration
        fields = ["id","created_at","declaration_date","name","declaration_no","net_weight",
                  "gross_weight","measurements","number_of_packages","regime_type","cargo_type","declaration_type","cargo_channel",
                  "transaction_type","trade_type","detail", "assign_user_id", "assign_user_name","items","status"]
    

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
    
    def get_assign_user_id(self, obj):
        return obj.assign_user_id

    def get_assign_user_name(self, obj):
        return obj.assign_user_name
    
    def get_status(self, obj):
        return obj.is_verified

    def get_items(self, obj):
        items = Items.objects.filter(declaration=obj)
        return ItemSerializer(items, many=True).data 
    
    
class DelcarationListSerilaizer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = Declaration
        fields = ["id","name","declaration_no","net_weight","measurements","created_at","assign_user_id", "assign_user_name","status"]


    def get_name(self, obj):
        return obj.request_no
    
    def get_status(self, obj):
        return obj.is_verified
    
    


class UpdateDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ["is_verified","updated_by_id"]

class ListDeclarationLogSerializer(serializers.ModelSerializer):
    declaration = DeclarationSerializer()
    class Meta:
        model = Declaration_log
        fields = ["status","comment","declaration","id","created_at","updated_at","is_deleted"]


class DeclarationDataContractSerializer:


   def __init__(self, data):
       self.registration_data = data
   def parse_data(self):
    status_map = {
           -1: "rejected",
            0: "underprocess",
            1: "approved",
            2: "on-hold",
            }
    print("is_verified",self.registration_data.is_verified)
    declaration_data = {
           "id": str(self.registration_data.id),
           "declarationDate": str(self.registration_data.declaration_date),
           "requestNo": self.registration_data.request_no,
           "declarationNo": self.registration_data.declaration_no,
           "netWeight": int(self.registration_data.net_weight),
           "grossWeight":int(self.registration_data.gross_weight),
           "measurements": str(self.registration_data.measurements),
           "nmbrOfPackages": self.registration_data.nmbr_of_packages,
           "cargoType": self.registration_data.cargo_type.name,
           "declarationType": self.registration_data.declaration_type.name,
           "cargoChannel": self.registration_data.cargo_channel.name,
           "transactionType": self.registration_data.transaction_type.name,
           "tradeType": self.registration_data.trade_type.name,
           "regimeType": self.registration_data.regime_type.name,
           "iamUserId": self.registration_data.iam_user_id,
           "is_verified":str(status_map.get(self.registration_data.is_verified)),

       }


    return declaration_data
   

class ItemDataContractSerializer:

    def __init__(self, item, declaration_id):
        self.registration_data = item
        self.declaration_id = declaration_id

    def parse_data(self):
        documents = Document.objects.filter(item=self.registration_data)
        
        # Convert document URLs into a single string, separated by commas
        doc_urls = ",".join([doc.file.url for doc in documents])
        
        item_data = {
            "id": str(self.registration_data.id),
            "goodsDescription": self.registration_data.goods_description,
            "staticQuantityUnit": str(self.registration_data.static_quantity_unit),
            "suppQuantityUnit": str(self.registration_data.supp_quantity_unit),
            "unitWeight": int(self.registration_data.unit_weight),
            "goodsValue": int(self.registration_data.goods_value),
            "cifValue": int(self.registration_data.cif_value),
            "dutyFee": int(self.registration_data.duty_fee),
            "hsCode": self.registration_data.hs_code.hs_code,
            "declarationId": str(self.declaration_id),
            "documents": doc_urls,  # Store URLs as a comma-separated string
        }
        
        return item_data