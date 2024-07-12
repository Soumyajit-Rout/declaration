from django import forms
from .models import Declaration,Items,Document
from django.forms import inlineformset_factory

class DeclarationForm(forms.ModelForm):

    class Meta:
        model = Declaration
        fields = [
            'declaration_date',
            'request_no',
            'declaration_no',
            'net_weight',
            'gross_weight',
            'measurements',
            'nmbr_of_packages',
            'cargo_type',
            'declaration_type',
            'cargo_channel',
            'transaction_type',
            'trade_type',
            'regime_type'
        ]
        widgets = {
            'declaration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'request_no': forms.TextInput(attrs={'class': 'form-control'},),
            'declaration_no': forms.TextInput(attrs={'class': 'form-control'}),
            'net_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'},),
            'gross_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'measurements': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'nmbr_of_packages': forms.NumberInput(attrs={'class': 'form-control'}),
            'cargo_type': forms.Select(attrs={'class': 'form-control'}),
            'declaration_type': forms.Select(attrs={'class': 'form-control'}),
            'cargo_channel': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'trade_type': forms.Select(attrs={'class': 'form-control'}),
            'regime_type': forms.Select(attrs={'class': 'form-control'}),
        }

    
class ItemForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = [
                  'goods_description',
                  'static_quantity_unit',
                  'supp_quantity_unit',
                  'unit_weight',
                  'goods_value',
                  'cif_value',
                  'duty_fee',
                  'declaration',
                  'hs_code',
                  ]  
        
class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = [
            'goods_description',
            'hs_code',
            'static_quantity_unit',
            'supp_quantity_unit',
            'unit_weight',
            'goods_value',
            'cif_value',
            'duty_fee',
            'declaration',         
        ]

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "file",
            "item",
        ]




ItemFormSet = inlineformset_factory(Declaration, Items,extra=1,form=ItemForm, can_delete=True)
ItemUpdateFormSet = inlineformset_factory(Declaration, Items, form=ItemUpdateForm, extra=0, can_delete=True)
DocumentFormSet = inlineformset_factory(Items,Document,extra=1,form=DocumentForm, can_delete=True)

