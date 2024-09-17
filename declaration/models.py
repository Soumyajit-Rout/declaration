from django.db import models
from DeclarationManagement.models import TimestampedUUIDModel
import uuid
from django.core.exceptions import ValidationError

# pylint: disable=E1101,W0702,E1133

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
     is_verified = models.IntegerField(null=True,blank=True)
     comments = models.TextField(max_length=200,null=True,blank=True)
     iam_user_id = models.CharField(max_length=100,null=True,blank=True)
     updated_by_id = models.CharField(max_length=100,null=True,blank=True)
     contract_address = models.CharField(max_length=200,null=True,blank=True)
     save_as_draft = models.BooleanField(default=False,blank=True)
     assign_user_id = models.CharField(null=True, default="", blank=True)
     assign_user_name = models.CharField(null=True, default="", blank=True)

class HsCode(TimestampedUUIDModel):
    keywords = models.TextField(max_length=200,null=True,blank=False)  
    hs_code = models.CharField(max_length=100,null=True,blank=False)
    description = models.TextField(max_length=200,null=True,blank=False)
    duty_fee = models.CharField(max_length=200,null=True,blank=True)
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
     created_by = models.BooleanField(default=False,blank=True)

class Opinion(models.Model):
    department_choices = (
        (1, 'Evaluation'),
        (2, 'Investigation'),
        (3, 'Inspection'),
        (4, 'Tariff'),
        (5, 'Audit'),
        (6, 'Amendment and Cancellation'),
        (7, 'Origin'),
        (8, 'Legal'),
    )
    status_choices = (
        (0, 'Under Review'),
        (1, 'Release'),
        (-1, 'On Hold'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    declaration_id = models.CharField(max_length=250)
    department_ids = models.JSONField(default=list)
    status = models.IntegerField(choices=status_choices, default=0)
    comment = models.CharField(max_length=250, null=True, blank=True)
    employee_id = models.CharField(max_length=250, null=True, blank=True)
    employee_name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opinons'

    def save(self, *args, **kwargs):
        valid_department_ids = [choice[0] for choice in self.department_choices]
        if not all(dept_id in valid_department_ids for dept_id in self.department_ids):
            raise ValidationError("One or more selected departments are invalid.")
        if self.status not in dict(self.status_choices):
            raise ValidationError(f"Invalid status: {self.status}")
        super(Opinion, self).save(*args, **kwargs)
