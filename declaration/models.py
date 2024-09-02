from django.db import models
from DeclarationManagement.models import TimestampedUUIDModel

class RegimeType(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
        return self.name

class TradeType(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
        return self.name

class TransactionType(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
        return self.name

class CargoChannel(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
        return self.name

class DeclarationType(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
        return self.name

class CargoType(TimestampedUUIDModel):
     name = models.CharField(max_length=50,null=True,blank=True)

     def __str__(self):
            return self.name

class Declaration(TimestampedUUIDModel):
     declaration_date = models.DateField(null=True,blank=False)
     request_no = models.CharField(max_length=50,null=True,blank=False)
     declaration_no = models.CharField(max_length=50,null=True,blank=False)
     net_weight = models.FloatField(null=True,blank=False)
     gross_weight = models.FloatField(null=True,blank=False)
     measurements = models.FloatField(null=True,blank=False)
     nmbr_of_packages = models.IntegerField(null=True,blank=False)
     cargo_type = models.ForeignKey(CargoType,on_delete=models.SET_NULL, null=True)
     declaration_type = models.ForeignKey(DeclarationType,on_delete=models.SET_NULL, null=True)
     cargo_channel = models.ForeignKey(CargoChannel,on_delete=models.SET_NULL, null=True)
     transaction_type = models.ForeignKey(TransactionType,on_delete=models.SET_NULL, null=True)
     trade_type = models.ForeignKey(TradeType,on_delete=models.SET_NULL, null=True)
     regime_type = models.ForeignKey(RegimeType,on_delete=models.SET_NULL, null=True)
     is_verified = models.IntegerField(default=0,null=True,blank=True)
     comments = models.TextField(max_length=200,null=True,blank=True)
     iam_user_id = models.CharField(max_length=100,null=True,blank=True)
     updated_by_id = models.CharField(max_length=100,null=True,blank=True)
     contract_address = models.CharField(max_length=200,null=True,blank=True)

class HsCode(TimestampedUUIDModel):
    keywords = models.TextField(max_length=200,null=True,blank=False)  
    hs_code = models.CharField(max_length=15,null=True,blank=False)
    description = models.TextField(max_length=200,null=True,blank=False)

    def __str__(self):
        return f'{self.hs_code} - { self.description}'

class Items(TimestampedUUIDModel):
    goods_description = models.TextField(max_length=200,null=True,blank=False)
    static_quantity_unit = models.FloatField(null=True,blank=False)
    supp_quantity_unit = models.FloatField(null=True,blank=False)
    unit_weight =  models.FloatField(null=True,blank=False)
    goods_value =  models.FloatField(null=True,blank=False)
    cif_value = models.FloatField(null=True,blank=False)   
    duty_fee = models.FloatField(null=True,blank=False)
    declaration = models.ForeignKey(Declaration,on_delete=models.CASCADE)
    hs_code = models.ForeignKey(HsCode,on_delete=models.SET_NULL, null=True)


class RequiredDoc(TimestampedUUIDModel):
    name = models.CharField(max_length=25,null=True,blank=False)
    hs_code = models.ForeignKey(HsCode,on_delete=models.CASCADE)
    format = models.CharField(max_length=25,null=True,blank=False)

class Document(TimestampedUUIDModel):
    file = models.FileField(null=True,blank=True,upload_to="documents")
    item = models.ForeignKey(Items,on_delete=models.CASCADE)
    required_doc = models.ForeignKey(RequiredDoc,on_delete=models.CASCADE,null=True)


class Declaration_log(TimestampedUUIDModel):
     status_choices = (
        (0, 0),
        (1, 1),
        (2, 2),
        (-1, -1),
    )
     declaration = models.ForeignKey(Declaration,on_delete=models.CASCADE)
     status = models.IntegerField(choices=status_choices,default=0)
     comment = models.CharField(max_length=250,null=True,blank=True)
