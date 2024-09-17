import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DeclarationManagement.settings')
django.setup()

from datetime import date
from declaration.models import Declaration, Items, CargoType, DeclarationType, CargoChannel, TransactionType, TradeType, RegimeType, HsCode,RequiredDoc,Document

def create_declaration_and_items():
    # Fetch or create necessary foreign key objects
    cargo_type = CargoType.objects.get_or_create(name='General Cargo')[0]
    declaration_type = DeclarationType.objects.get_or_create(name='Import')[0]
    cargo_channel = CargoChannel.objects.get_or_create(name='Sea')[0]
    transaction_type = TransactionType.objects.get_or_create(name='Sale')[0]
    trade_type = TradeType.objects.get_or_create(name='International')[0]
    regime_type = RegimeType.objects.get_or_create(name='Normal')[0]

    # Create a new Declaration object
    declaration1 = Declaration.objects.create(
        declaration_date=date.today(),
        request_no='REQ123456',
        declaration_no='DECL123456',
        net_weight=1000.0,
        gross_weight=1200.0,
        measurements=50.0,
        nmbr_of_packages=10,
        cargo_type=cargo_type,
        declaration_type=declaration_type,
        cargo_channel=cargo_channel,
        transaction_type=transaction_type,
        trade_type=trade_type,
        regime_type=regime_type,
        is_verified=0,
        iam_user_id='0fedbdc71b2793aa',
    )

    declaration2 = Declaration.objects.create(
        declaration_date=date.today(),
        request_no='QES49495',
        declaration_no='YUTU7898',
        net_weight=1000.0,
        gross_weight=1200.0,
        measurements=50.0,
        nmbr_of_packages=10,
        cargo_type=cargo_type,
        declaration_type=declaration_type,
        cargo_channel=cargo_channel,
        transaction_type=transaction_type,
        trade_type=trade_type,
        regime_type=regime_type,
        is_verified=0,
        iam_user_id='0fedbdc71b2793aa',
    )

    # Fetch or create HsCode objects
    hs_code_1 = HsCode.objects.get_or_create(hs_code='0401', description=' Milk and cream, not concentrated nor containing added sugar or other sweetening matter, of a fat content by weight not exceeding 1%.',keywords='milk,cream')[0]
    hs_code_2 = HsCode.objects.get_or_create(hs_code='0302', description='Fish, fresh or chilled, cod (excluding fillets, livers, and roes)',keywords='fish,seafood')[0]

    # Create Items related to the declaration
    item_1 = Items.objects.create(
        goods_description='Milk and cream, not concentrated nor containing added sugar or other sweetening matter, of a fat content by weight not exceeding 1%.',
        static_quantity_unit=20,
        supp_quantity_unit=15,
        unit_weight=100.0,
        goods_value=50000.0,
        cif_value=52000.0,
        duty_fee=500.0,
        declaration=declaration1,
        hs_code=hs_code_1
    )

    item_2 = Items.objects.create(
        goods_description='Fish, fresh or chilled, cod (excluding fillets, livers, and roes)',
        static_quantity_unit=50,
        supp_quantity_unit=45,
        unit_weight=200.0,
        goods_value=100000.0,
        cif_value=102000.0,
        duty_fee=2000.0,
        declaration=declaration2,
        hs_code=hs_code_2
    )
    required_doc_1 = RequiredDoc.objects.get_or_create(
        name = 'dairy',
        hs_code=hs_code_1,
        format='pdf'
    )[0]
    required_doc_2 =  RequiredDoc.objects.get_or_create(
        name = 'meat',
        hs_code=hs_code_2,
        format='pdf'
    )[0]
    document_1 = Document.objects.create(
        file='documents/oreo.pdf',  
        item=item_1,
        required_doc=required_doc_1
    )

    document_2 = Document.objects.create(
        file='documents/lays.pdf', 
        item=item_2,
        required_doc=required_doc_2
    )


    print("Data added successfully")

# Run the function
if __name__ == "__main__":
    create_declaration_and_items()