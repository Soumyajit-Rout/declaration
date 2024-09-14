import logging
import os
import threading


import requests
from celery import shared_task
from django.conf import settings
from django.shortcuts import get_object_or_404
from substrateinterface import Keypair, SubstrateInterface
from substrateinterface.contracts import ContractCode, ContractInstance
import random
import string
from .models import Declaration,Items,HsCode,Document
from .serializers import DeclarationDataContractSerializer,ItemDataContractSerializer


logger = logging.getLogger("custom_logger")
# pylint: disable=E1101,W0702




@shared_task
def get_id(id):
   try:
       logger.debug(f"Starting get_id with id: {id[0]}")
       data = get_object_or_404(Declaration, id=id[0])
       items_data = Items.objects.filter(declaration=data)
       logger.debug("CompanyRegistration object retrieved successfully")


       declaration_data = DeclarationDataContractSerializer(
           data
       ).parse_data()
       logger.debug("Declaration data serialized successfully")

       items_datas = [ItemDataContractSerializer(item,declaration_id=data.id).parse_data() for item in items_data]
       logger.debug("Items data serialized successfully")

       logger.debug(
           "Starting send_declaration_info_to_contract in a new thread"
       )
       thread = threading.Thread(
           target=send_company_registration_info_to_contract,
           args=(declaration_data,items_datas),
       )
       thread.start()


       logger.debug("Thread started successfully")
       return declaration_data, items_datas


   except Declaration.DoesNotExist:
       error_message = {"error": "Declaration details not found"}
       logger.error(error_message)
       print(error_message)
   except Exception as e:
       error_message = {"error": "Internal server error", "details": str(e)}
       logger.error(error_message)
       print(error_message)




@shared_task
def send_company_registration_info_to_contract(declaration_data,items_data):
   try:
       declaration_info = {
           "_id": declaration_data.get("id"),
           "_declaration_date": declaration_data.get("declarationDate"),
           "_request_no": declaration_data.get("requestNo"),
           "_declaration_no": declaration_data.get("declarationNo"),
           "_net_weight": declaration_data.get("netWeight"),
           "_gross_weight": declaration_data.get("grossWeight"),
           "_measurements": declaration_data.get("measurements"),
           "_nmbr_of_packages": declaration_data.get("nmbrOfPackages"),
           "_cargo_type": declaration_data.get("cargoType"),
           "_declaration_type": declaration_data.get("declarationType"),
           "_cargo_channel": declaration_data.get("cargoChannel"),
           "_transaction_type": declaration_data.get("transactionType"),
           "_trade_type": declaration_data.get("tradeType"),
           "_regime_type": declaration_data.get("regimeType"),
           "_iam_user_id": declaration_data.get("iamUserId"),
           "_comments":" ",
           "_is_verified":" ",
           "_updated_by_user":" ",
       }
       substrate = SubstrateInterface(url="wss://contract-node.finloge.com/")
       keypair = Keypair.create_from_uri("//Alice")
    


       try:
        
               code = ContractCode.create_from_contract_files(
                   metadata_file=os.path.join(
                       os.path.dirname(__file__),
                       "static",
                       "assets",
                       "CargoDeclaration.contract",
                   ),
                   wasm_file=os.path.join(
                       os.path.dirname(__file__),"static","assets", "CargoDeclaration.wasm"
                   ),
                   substrate=substrate,
               )


               logger.info("Deploying contract.......")
               salt = generate_salt()

               contract = code.deploy(
                    keypair=keypair,
                    constructor="new",
                    value=0,
                    gas_limit={
                        "ref_time": 78387347456,
                        "proof_size": 2097152,
                    },
                    deployment_salt=salt,
                    upload_code=False,
                )
               contract_address = contract.contract_address
               id = declaration_data.get("id")
               declaration = Declaration.objects.get(id=id)
               declaration.contract_address = contract_address
               declaration.save()
               

       except Exception as e:
           print(f"Failed to query or deploy contract: {str(e)}")
           logger.error(f"Failed to query or deploy contract: {str(e)}")
           return False


       try:
           logger.info("Creating contract.......")
           request_save_declaration = contract.exec(
               keypair, "addDeclaration", args={**declaration_info}
           )

           logger.info(f"Contract execution result: {request_save_declaration.block_hash}")
            
           if request_save_declaration.is_success:
               logger.info(f"Success hash: {request_save_declaration.extrinsic_hash}")
               print(f"Success hash: {request_save_declaration.extrinsic_hash}")
               for item in items_data:
                item_info = {
                    "_id": item.get("id"),
                    "_goods_description": item.get("goodsDescription"),
                    "_static_quantity_unit": item.get("staticQuantityUnit"),
                    "_supp_quantity_unit": item.get("suppQuantityUnit"),
                    "_unit_weight": item.get("unitWeight"),
                    "_goods_value": item.get("goodsValue"),
                    "_cif_value": item.get("cifValue"),
                    "_duty_fee": item.get("dutyFee"),
                    "_hs_code": item.get("hsCode"),
                    "_declaration_id": item.get("declarationId"),
                    "_documents": item.get("documents"),
                }

                request_save_item = contract.exec(
                    keypair, "addItem", args={**item_info}
                )

                if request_save_item.is_success:
                    logger.info(f"Item added successfully with hash: {request_save_item.extrinsic_hash}")
                else:
                    logger.error(f"Failed to add item: {request_save_item.error_message}")

               # Save the contract data in blockchain database
               logger.debug("Sending save request to blockchain explorer")
               data = {
                   "dataId": declaration_data.get("id"),
                   "contractAddress": contract_address,
                   "contractType": "declaration",
               }
               headers = {
                   "Authorization": f"Bearer {settings.STATIC_API_TOKEN}",
               }
               response = requests.post(
                   settings.CUSTOM_BLOCKCHAIN_SMART_CONTRACT_URL,
                   json=data,
                   headers=headers,
                   timeout=3,
               )
               if response.status_code == 201 or response.status_code == 200:
                   logger.info("Successful:%s", response.text)
               else:
                   logger.error(
                       "Failed to create data in blockchain db. Status code: %s.Error Response: %s",
                       response.status_code,
                       response.text,
                   )
           else:
               logger.error(f"Execution failed: {request_save_declaration.error_message}")
               print(f"Execution failed: {request_save_declaration.error_message}")


           return request_save_declaration.is_success
       except Exception as e:
           logger.error(f"Failed to execute or read contract: {str(e)}")
           print(f"Failed to execute or read contract: {str(e)}")
           return False


   except Exception as e:
       print(f"Unexpected error: {str(e)}")
       logger.error(f"Unexpected error: {str(e)}")
       return False

@shared_task
def update_declaration_info_to_contract(id):

    try:
       data = get_object_or_404(Declaration, id=id)
       
       declaration_data = DeclarationDataContractSerializer(
           data
       ).parse_data()
       contract_address = data.contract_address
       print("contract_address",contract_address)
       
       declaration_update_info = {
           "_newStatus": declaration_data.get("is_verified"),
           "_declarationId": declaration_data.get("id"),
       }
       substrate = SubstrateInterface(url="wss://contract-node.finloge.com/")
       keypair = Keypair.create_from_uri("//Alice")

       try:
            contract_info = substrate.query(
               "Contracts", "ContractInfoOf", [contract_address]
           )
            if contract_info.value:
               logger.info("Found contract on chain: %s", contract_info.value)
               contract = ContractInstance.create_from_address(
                   contract_address=contract_address,
                   metadata_file=os.path.join(
                       os.path.dirname(__file__),
                       "static",
                       "assets",
                       "CargoDeclaration.contract",
                   ),
                   substrate=substrate,
               )

            else:
               code = ContractCode.create_from_contract_files(
                   metadata_file=os.path.join(
                       os.path.dirname(__file__),
                       "static",
                       "assets",
                       "CargoDeclaration.contract",
                   ),
                   wasm_file=os.path.join(
                       os.path.dirname(__file__),"static","assets", "CargoDeclaration.wasm"
                   ),
                   substrate=substrate,
               )

               logger.info("Deploying contract.......")
               salt = generate_salt()

               contract = code.deploy(
                    keypair=keypair,
                    constructor="new",
                    value=0,
                    gas_limit={
                        "ref_time": 78387347456,
                        "proof_size": 2097152,
                    },
                    deployment_salt=salt,
                    upload_code=False,
                )
               contract_address = contract.contract_address

       except Exception as e:
           print(f"Failed to query or deploy contract: {str(e)}")
           logger.error(f"Failed to query or deploy contract: {str(e)}")
           return False


       try:
           logger.info("Creating contract.......")
           print("update",declaration_update_info)
           print("declaration_data--------",declaration_data.get("is_verified"))

           request_save_declaration = contract.exec(
               keypair,"updateIsVerified", args={**declaration_update_info}
           )

           logger.info(f"Contract execution result: {request_save_declaration.block_hash}")
            
           if request_save_declaration.is_success:           

               # Save the contract data in blockchain database
               logger.debug("Sending save request to blockchain explorer")
            
           else:
               logger.error(f"Execution failed: {request_save_declaration.error_message}")
               print(f"Execution failed: {request_save_declaration.error_message}")


           return request_save_declaration.is_success
       except Exception as e:
           logger.error(f"Failed to execute or read contract: {str(e)}")
           print(f"Failed to execute or read contract: {str(e)}")
           return False


    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return False



@shared_task
def get_updated_id(id):
   try:
       data = get_object_or_404(Declaration, id=id)
       items_data = Items.objects.filter(declaration=data)
       logger.debug("CompanyRegistration object retrieved successfully")

       declaration_data = DeclarationDataContractSerializer(
           data
       ).parse_data()
       logger.debug("Declaration data serialized successfully")

       items_datas = [ItemDataContractSerializer(item,declaration_id=data.id).parse_data() for item in items_data]
       logger.debug("Items data serialized successfully")

       logger.debug(
           "Starting send_declaration_info_to_contract in a new thread"
       )
       thread = threading.Thread(
           target=update_declaration_to_contract,
           args=(declaration_data,items_datas),
       )
       thread.start()


       logger.debug("Thread started successfully")
       return declaration_data, items_datas


   except Declaration.DoesNotExist:
       error_message = {"error": "Declaration details not found"}
       logger.error(error_message)
       print(error_message)
   except Exception as e:
       error_message = {"error": "Internal server error", "details": str(e)}
       logger.error(error_message)
       print(error_message)


@shared_task
def update_declaration_to_contract(declaration_data,items_data):
   try:
       id = declaration_data.get("id")
       data = get_object_or_404(Declaration, id=id)
       contract_address = data.contract_address
       print("contract_address",contract_address)
       declaration_info = {
           "_id": declaration_data.get("id"),
           "_declaration_date": declaration_data.get("declarationDate"),
           "_request_no": declaration_data.get("requestNo"),
           "_declaration_no": declaration_data.get("declarationNo"),
           "_net_weight": declaration_data.get("netWeight"),
           "_gross_weight": declaration_data.get("grossWeight"),
           "_measurements": declaration_data.get("measurements"),
           "_nmbr_of_packages": declaration_data.get("nmbrOfPackages"),
           "_cargo_type": declaration_data.get("cargoType"),
           "_declaration_type": declaration_data.get("declarationType"),
           "_cargo_channel": declaration_data.get("cargoChannel"),
           "_transaction_type": declaration_data.get("transactionType"),
           "_trade_type": declaration_data.get("tradeType"),
           "_regime_type": declaration_data.get("regimeType"),
           "_iam_user_id": declaration_data.get("iamUserId"),
           "_comments":" ",
           "_is_verified":" ",
           "_updated_by_user":" ",
       }
       substrate = SubstrateInterface(url="wss://contract-node.finloge.com/")
       keypair = Keypair.create_from_uri("//Alice")


       try:
            contract_info = substrate.query(
               "Contracts", "ContractInfoOf", [contract_address]
           )
            if contract_info.value:
               logger.info("Found contract on chain: %s", contract_info.value)
               contract = ContractInstance.create_from_address(
                   contract_address=contract_address,
                   metadata_file=os.path.join(
                       os.path.dirname(__file__),
                       "static",
                       "assets",
                       "CargoDeclaration.contract",
                   ),
                   substrate=substrate,
               )

            else:
               code = ContractCode.create_from_contract_files(
                   metadata_file=os.path.join(
                       os.path.dirname(__file__),
                       "static",
                       "assets",
                       "CargoDeclaration.contract",
                   ),
                   wasm_file=os.path.join(
                       os.path.dirname(__file__),"static","assets", "CargoDeclaration.wasm"
                   ),
                   substrate=substrate,
               )

               logger.info("Deploying contract.......")
               salt = generate_salt()

               contract = code.deploy(
                    keypair=keypair,
                    constructor="new",
                    value=0,
                    gas_limit={
                        "ref_time": 78387347456,
                        "proof_size": 2097152,
                    },
                    deployment_salt=salt,
                    upload_code=False,
                )
               contract_address = contract.contract_address
               id = declaration_data.get("id")
               declaration = Declaration.objects.get(id=id)
               declaration.contract_address = contract_address
               declaration.save()
               

       except Exception as e:
           print(f"Failed to query or deploy contract: {str(e)}")
           logger.error(f"Failed to query or deploy contract: {str(e)}")
           return False


       try:
           logger.info("Creating contract.......")
           request_save_declaration = contract.exec(
               keypair, "updateDeclaration", args={**declaration_info}
           )

           logger.info(f"Contract execution result: {request_save_declaration.block_hash}")
            
           if request_save_declaration.is_success:
               logger.info(f"Success hash: {request_save_declaration.extrinsic_hash}")
               print(f"Success hash: {request_save_declaration.extrinsic_hash}")
               for item in items_data:
                item_info = {
                    "_id": item.get("id"),
                    "_goods_description": item.get("goodsDescription"),
                    "_static_quantity_unit": item.get("staticQuantityUnit"),
                    "_supp_quantity_unit": item.get("suppQuantityUnit"),
                    "_unit_weight": item.get("unitWeight"),
                    "_goods_value": item.get("goodsValue"),
                    "_cif_value": item.get("cifValue"),
                    "_duty_fee": item.get("dutyFee"),
                    "_hs_code": item.get("hsCode"),
                    "_declaration_id": item.get("declarationId"),
                    "_documents": item.get("documents"),
                }

                request_save_item = contract.exec(
                    keypair, "updateItem", args={**item_info}
                )

                if request_save_item.is_success:
                    logger.info(f"Item added successfully with hash: {request_save_item.extrinsic_hash}")
                else:
                    logger.error(f"Failed to add item: {request_save_item.error_message}")

           else:
               logger.error(f"Execution failed: {request_save_declaration.error_message}")
               print(f"Execution failed: {request_save_declaration.error_message}")


           return request_save_declaration.is_success
       except Exception as e:
           logger.error(f"Failed to execute or read contract: {str(e)}")
           print(f"Failed to execute or read contract: {str(e)}")
           return False


   except Exception as e:
       print(f"Unexpected error: {str(e)}")
       logger.error(f"Unexpected error: {str(e)}")
       return False



def generate_salt(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@shared_task
def sent_items_to_ai(id):
    print("declaration_id",id)
    declaration_data = get_object_or_404(Declaration, id=id) 
    data = Items.objects.filter(declaration=declaration_data)
    items_data = []
    for item in data:
        print("loop1")
        hs_code = item.hs_code.hs_code
        item_data = {
            "HS Code": hs_code,
            "Item Description": item.goods_description,
            "Country of Origin": "other",  
            "Declared Value (USD)": item.duty_fee,  
            "Quantity": item.static_quantity_unit,
            "Weight (kg)": item.supp_quantity_unit,
            "Previous Risk Flag": "other" 
        }
        items_data.append(item_data)
        print("items_data",items_data)
    
        api_url = settings.AI_URL
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, json=items_data, headers=headers)
        response_data = response.json()['predictions']
        if 'High' in response_data:
            declaration_data.is_verified = 0
            declaration_data.save()
        else:
            declaration_data.is_verified = 1
            declaration_data.save()

        print("response_data",response_data)
        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}: {response.text}")
        else:
            print(f"API response: {response.json()}")  