from django.contrib import admin

# Register your models here.
from .models import *


class DeclarationAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'declaration_type',
          'declaration_no',
     )


class CargoTypeAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )


class DeclarationTypeAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )


class CargoChannelAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )


class TransactionTypeAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )


class TradeTypeAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )


class RegimeTypeAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'name',
     )
class ItemsAdmin(admin.ModelAdmin):
     list_display = (
          'created_at',
          'updated_at',
          'id',
          'goods_value',
          'is_deleted'
     )

admin.site.register(Declaration, DeclarationAdmin)
admin.site.register(CargoType, CargoTypeAdmin)
admin.site.register(DeclarationType, DeclarationTypeAdmin)
admin.site.register(CargoChannel, CargoChannelAdmin)
admin.site.register(TradeType, TradeTypeAdmin)
admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(RegimeType, RegimeTypeAdmin)
admin.site.register(Items, ItemsAdmin)



