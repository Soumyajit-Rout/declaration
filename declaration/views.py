from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from .serializers import *
from .forms import DeclarationForm,ItemFormSet,ItemUpdateFormSet,DocumentFormSet,DeclarationUpdateForm
from django.db import transaction
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from rest_framework import generics
from .permissions import StaticTokenPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
import requests
from .tasks import get_id,update_declaration_info_to_contract,get_updated_id,sent_items_to_ai
from rest_framework.views import APIView
from rest_framework import renderers, status
from rest_framework.response import Response
from urllib.request import Request
from DeclarationManagement.utils import Authentication
from django.forms.models import model_to_dict

# pylint: disable=E1101,W0702,E1133



"""
This function is to create a declaration form along with the items,here with each
declaration object multiple items get saved to the database ,that is done using django's
formset technique,apart from the normal post functionality here atomicity has also been 
implemented
"""

def create_declaration(request):
    if request.method == 'POST':
        declaration_form = DeclarationForm(request.POST)
        item_formset = ItemFormSet(request.POST)
        # document_formset = DocumentFormSet(request.POST, request.FILES)
        if declaration_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    user_id = request.session.get('id', None)
                    declaration = declaration_form.save(commit=False)
                              
                    if user_id:
                        declaration.iam_user_id = user_id
                    if 'save_draft' in request.POST:
                        declaration.save_as_draft = True
                        declaration.is_verified = 3
                    else:
                        declaration.save_as_draft = False

                    declaration.save()

                    item_formset.instance = declaration
                    items = item_formset.save()         
                    for item_index, item in enumerate(items):
                        hs_code = item.hs_code
                        if hs_code:
                            required_docs = RequiredDoc.objects.filter(hs_code=hs_code)
                            for req_doc in required_docs:
                                file_field_name = f'documents_{item_index}_{req_doc.id}'
                                
                                if file_field_name in request.FILES:

                                    Document.objects.create(
                                        item=item,
                                        file=request.FILES[file_field_name],
                                        required_doc = req_doc
                                    )
                    get_id.delay((declaration.id,))
                    if not declaration.save_as_draft:
                        sent_items_to_ai.delay(declaration.id)
                # Declaration_log.objects.create(declaration=declaration,status=declaration.is_verified)
                messages.success(request, 'Declaration added successfully.')
                return redirect('view_declaration')
            except Exception as e:
                print(e)
                declaration_form.add_error(None, 'An error occurred while saving items.')
    else:
        declaration_form = DeclarationForm()
        item_formset = ItemFormSet()

    return render(request, 'create_declaration.html', {
        'form': declaration_form,
        'item_formset': item_formset,
    })
"""
This function is to display the declaration objects it is a normal list function and
renders the view_declaration.html page
"""
def declaration_list(request):
                    
    user_id = request.session.get('id')
    declarations = Declaration.objects.filter(is_deleted=False,iam_user_id=user_id).order_by('declaration_date')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(declarations, 3) 
    try:
        declarations = paginator.page(page)
    except PageNotAnInteger:
        declarations = paginator.page(1)
    except EmptyPage:
        declarations = paginator.page(paginator.num_pages)
    
    return render(request, 'view_declaration.html', {'declarations': declarations})

"""
This function is to update the declaration form as well as the item objects,here the 
function expects an id of the declaration object,once the updation is completed,the 
page gets redirected to view_declaration page and here the page which is being rendered is
the update_declaration.html
"""

def update_declaration(request, pk):
    declaration = get_object_or_404(Declaration, id=pk)

    if request.method == 'POST':
        # Manually retrieve data from request.POST
        cargo_type_id = request.POST.get('cargo_type')
        declaration_type_id = request.POST.get('declaration_type')
        cargo_channel_id = request.POST.get('cargo_channel')
        transaction_type_id = request.POST.get('transaction_type')
        trade_type_id = request.POST.get('trade_type')
        regime_type_id = request.POST.get('regime_type')

        # Fetch model instances
        cargo_type = CargoType.objects.get(id=cargo_type_id) if cargo_type_id else None
        declaration_type = DeclarationType.objects.get(id=declaration_type_id) if declaration_type_id else None
        cargo_channel = CargoChannel.objects.get(id=cargo_channel_id) if cargo_channel_id else None
        transaction_type = TransactionType.objects.get(id=transaction_type_id) if transaction_type_id else None
        trade_type = TradeType.objects.get(id=trade_type_id) if trade_type_id else None
        regime_type = RegimeType.objects.get(id=regime_type_id) if regime_type_id else None

        declaration_data = {
            'declaration_date': request.POST.get('declaration_date'),
            'request_no': request.POST.get('request_no'),
            'declaration_no': request.POST.get('declaration_no'),
            'net_weight': request.POST.get('net_weight'),
            'gross_weight': request.POST.get('gross_weight'),
            'measurements': request.POST.get('measurements'),
            'nmbr_of_packages': request.POST.get('nmbr_of_packages'),
            'cargo_type': cargo_type,
            'declaration_type': declaration_type,
            'cargo_channel': cargo_channel,
            'transaction_type': transaction_type,
            'trade_type': trade_type,
            'regime_type': regime_type,
            'comments': request.POST.get('comments'),
        }

        # Manually update declaration object
        for field, value in declaration_data.items():
            setattr(declaration, field, value)
        declaration.save()

        # Update items
        items_data = []
        item_ids = request.POST.getlist('items_set-id')


        for idx, item_id in enumerate(item_ids):
            hs_code_id = request.POST.get(f'items_set-{idx}-hs_code')
            hs_code = HsCode.objects.get(id=hs_code_id) if hs_code_id else None
            item_data = {
                'goods_description': request.POST.get(f'items_set-{idx}-description'),
                'hs_code': hs_code,
                'static_quantity_unit': request.POST.get(f'items_set-{idx}-static_quantity_unit'),
                'supp_quantity_unit': request.POST.get(f'items_set-{idx}-supp_quantity_unit'),
                'unit_weight': request.POST.get(f'items_set-{idx}-unit_weight'),
                'goods_value': request.POST.get(f'items_set-{idx}-goods_value'),
                'cif_value': request.POST.get(f'items_set-{idx}-cif_value'),
                'duty_fee': request.POST.get(f'items_set-{idx}-duty_fee'),
            }
            items_data.append((item_id, item_data))

        for item_id, item_data in items_data:
            item = get_object_or_404(Items, id=item_id, declaration=declaration)
            for field, value in item_data.items():
                setattr(item, field, value)
            item.save()

        # Handle documents
        pattern = re.compile(r'documents_item_(?P<item_id>[a-fA-F0-9\-]+)_(?P<doc_id>[a-fA-F0-9\-]+)')
        new_pattern = re.compile(r'new_documents_(?P<item_id>[a-fA-F0-9\-]+)_(?P<doc_id>[a-fA-F0-9\-]+)')
        doc = []

        for key, file in request.FILES.items():
            if key.startswith('documents_item'):
                match = pattern.match(key)
                if match:
                    item_id = match.group('item_id')
                    doc_id = match.group('doc_id')
                    item_obj = get_object_or_404(Items, id=item_id)
                    required_doc = get_object_or_404(RequiredDoc, id=doc_id)

                    # Check if the document already exists
                    document, created = Document.objects.get_or_create(
                        item=item_obj,
                        required_doc=required_doc,
                        defaults={'file': file}
                    )

                    if not created:
                        # Update the existing document
                        if document.file != file:
                            document.file = file
                            document.save()

            elif key.startswith('new_documents'):
                match = new_pattern.match(key)
                if match:
                    item_id = match.group('item_id')
                    doc_id = match.group('doc_id')
                    item_obj = get_object_or_404(Items, id=item_id)
                    required_doc = get_object_or_404(RequiredDoc, id=doc_id)
                    doc.append(required_doc)
                    existing_documents = Document.objects.filter(item=item_obj).exclude(required_doc__in=doc)


                    if existing_documents.exists():
                        existing_documents.update(is_deleted=True)

                    Document.objects.create(item=item_obj,
                                            file=request.FILES[key],
                                            required_doc=required_doc
                                            )
        declaration.save()
        sent_items_to_ai.delay(declaration.id)
        get_updated_id.delay((declaration.id))
        messages.success(request, 'Declaration updated successfully.')            
        # Redirect to prevent resubmission
        return redirect('view_declaration')

    else:
        # Populate initial data for the form
        regime_types = RegimeType.objects.all()
        trade_types = TradeType.objects.all()
        transaction_types = TransactionType.objects.all()
        cargo_channels = CargoChannel.objects.all()
        declaration_types = DeclarationType.objects.all()
        cargo_types = CargoType.objects.all()
        hs_codes = HsCode.objects.all()

        declaration_data = {
            'declaration_date': declaration.declaration_date,
            'request_no': declaration.request_no,
            'declaration_no': declaration.declaration_no,
            'net_weight': declaration.net_weight,
            'gross_weight': declaration.gross_weight,
            'measurements': declaration.measurements,
            'nmbr_of_packages': declaration.nmbr_of_packages,
            'cargo_type': declaration.cargo_type,
            'declaration_type': declaration.declaration_type,
            'cargo_channel': declaration.cargo_channel,
            'transaction_type': declaration.transaction_type,
            'trade_type': declaration.trade_type,
            'regime_type': declaration.regime_type,
            'comments': declaration.comments,
            'regime_types': regime_types,
            'trade_types': trade_types,
            'transaction_types': transaction_types,
            'cargo_channels': cargo_channels,
            'declaration_types': declaration_types,
            'cargo_types': cargo_types,
        }
        items_data = []
        for item in declaration.items_set.filter(is_deleted=False):
            items_data.append({
                'id': item.id,
                'description': item.goods_description,
                'hs_code': item.hs_code,
                'static_quantity_unit': item.static_quantity_unit,
                'supp_quantity_unit': item.supp_quantity_unit,
                'unit_weight': item.unit_weight,
                'goods_value': item.goods_value,
                'cif_value': item.cif_value,
                'duty_fee': item.duty_fee,
            })

        document_formsets = []
        for item in declaration.items_set.all():
            document_formset = []
            for doc in item.document_set.filter(is_deleted=False):
                document_formset.append({
                    'id': doc.id,
                    'file': doc.file,
                    'required_doc': doc.required_doc,
                })
            document_formsets.append({
                'item': item,
                'documents': document_formset,
            })
    declaration_log = Declaration_log.objects.filter(declaration=declaration,created_by = True).order_by('-created_at').first()
    context = {
        'declaration_data': declaration_data,
        'items_data': items_data,
        'document_formsets': document_formsets,
        'regime_types': regime_types,
        'trade_types': trade_types,
        'transaction_types': transaction_types,
        'cargo_channels': cargo_channels,
        'declaration_types': declaration_types,
        'cargo_types': cargo_types,
        'hs_codes': hs_codes,
        'declaration_log':declaration_log,
    }

    return render(request, 'update_declarations.html', context)


"""
This is to soft delete the declaraion object when the delete button in the update html
page is clicked this function gets called and the is_deleted field within the object is
made to true .
"""
def delete_declaration(request, pk):
    declaration = Declaration.objects.get(id=pk)
    declaration.is_deleted = True
    declaration.save()
    return redirect('view_declaration')



def list_declaration(request,pk):
        declaration = Declaration.objects.get(id=pk)
      # Populate initial data for the form
        regime_types = RegimeType.objects.all()
        trade_types = TradeType.objects.all()
        transaction_types = TransactionType.objects.all()
        cargo_channels = CargoChannel.objects.all()
        declaration_types = DeclarationType.objects.all()
        cargo_types = CargoType.objects.all()
        hs_codes = HsCode.objects.all()

        declaration_data = {
            'declaration_date': declaration.declaration_date,
            'request_no': declaration.request_no,
            'declaration_no': declaration.declaration_no,
            'net_weight': declaration.net_weight,
            'gross_weight': declaration.gross_weight,
            'measurements': declaration.measurements,
            'nmbr_of_packages': declaration.nmbr_of_packages,
            'cargo_type': declaration.cargo_type,
            'declaration_type': declaration.declaration_type,
            'cargo_channel': declaration.cargo_channel,
            'transaction_type': declaration.transaction_type,
            'trade_type': declaration.trade_type,
            'regime_type': declaration.regime_type,
            'comments': declaration.comments,
            'declaration_types': declaration.declaration_type,
            'cargo_types': declaration.cargo_type,
        }
        items_data = []
        for item in declaration.items_set.filter(is_deleted=False):
            items_data.append({
                'id': item.id,
                'description': item.goods_description,
                'hs_code': item.hs_code,
                'static_quantity_unit': item.static_quantity_unit,
                'supp_quantity_unit': item.supp_quantity_unit,
                'unit_weight': item.unit_weight,
                'goods_value': item.goods_value,
                'cif_value': item.cif_value,
                'duty_fee': item.duty_fee,
            })

        document_formsets = []
        for item in declaration.items_set.all():
            document_formset = []
            for doc in item.document_set.filter(is_deleted=False):
                document_formset.append({
                    'id': doc.id,
                    'file': doc.file,
                    'required_doc': doc.required_doc,
                })
            document_formsets.append({
                'item': item,
                'documents': document_formset,
            })

        context = {
            'declaration_data': declaration_data,
            'items_data': items_data,
            'document_formsets': document_formsets,
            'hs_codes': hs_codes,
        }

        return render(request, 'retrieve_declaration.html', context)

"""
This function is to search for the hscodes based on the description text here we will convert 
the text into a list of items and query the database to match the list of words with the 
keywords in the hscode 
"""
@csrf_exempt
@require_POST
def search_hscode(request):
    data = json.loads(request.body)
    description = data.get('description', '').lower()
    hs_codes = []
    if description:
        description_data = re.findall(r'\b\w+\b', description)
        hs_codes_set = set()
        for word in description_data:
            matching_hs_codes = HsCode.objects.filter(
                keywords__icontains=word  
            )
            for hs_code in matching_hs_codes:
                if word in hs_code.keywords.split(','):
                    hs_codes_set.add(hs_code)

        
        for hs_code in hs_codes_set:
            hs_codes.append({
                'id': hs_code.id,
                'hs_code': hs_code.hs_code,
                'description': hs_code.description
            })
    else :
        matching_hs_codes = HsCode.objects.all()
        for hs_code in matching_hs_codes:
             hs_codes.append({
                'id': hs_code.id,
                'hs_code': hs_code.hs_code,
                'description': hs_code.description
            })
    
    return JsonResponse({'hs_codes': hs_codes})


@csrf_exempt
@require_POST
def update_search_hscode(request,pk):
    item_obj = Items.objects.get(id=pk)
    hs_code_id  = item_obj.hs_code.id
    data = json.loads(request.body)
    description = data.get('description', '').lower()
    hs_codes = []
    if description:
        description_data = re.findall(r'\b\w+\b', description)
        hs_codes_set = set()
        for word in description_data:
            matching_hs_codes = HsCode.objects.filter(
                keywords__icontains=word  
            ).exclude(id = hs_code_id)
            for hs_code in matching_hs_codes:
                if word in hs_code.keywords.split(','):
                    hs_codes_set.add(hs_code)

        
        for hs_code in hs_codes_set:
            hs_codes.append({
                'id': hs_code.id,
                'hs_code': hs_code.hs_code,
                'description': hs_code.description
            })
    else :
        matching_hs_codes = HsCode.objects.all()
        for hs_code in matching_hs_codes:
             hs_codes.append({
                'id': hs_code.id,
                'hs_code': hs_code.hs_code,
                'description': hs_code.description
            })
    
    return JsonResponse({'hs_codes': hs_codes})

"""
Basic api to list the declarations 
"""
class ListDeclarations(generics.ListAPIView):
    permission_classes = [StaticTokenPermission]
    serializer_class = DelcarationListSerilaizer

    def get_queryset(self):
            return Declaration.objects.filter(is_verified=0).order_by('-updated_at')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": status.HTTP_200_OK,"registration_data": serializer.data})

"""
Basic api to retrieve the declarations based on id 
"""

class RetrieveDeclaration(APIView):
    permission_classes = [StaticTokenPermission]

    def get(self, request):
        id = request.query_params.get("id")
        if not id:
            return Response({"detail": "ID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            declaration = Declaration.objects.get(is_verified=0, id=id)
            opinion_data = Opinion.objects.filter(
                declaration_id=id
            ).order_by("-created_at")
            opinions = []
            if opinion_data:
                for obj in opinion_data:
                    entry = model_to_dict(obj)
                    opinions.append(entry)
        except Declaration.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeclarationSerializer(declaration)
        return Response({"status":status.HTTP_200_OK,"registration_data":serializer.data, "opinions": opinions})
    
"""
Basic api to update the declarations based on id 
"""
class UpdateDeclaration(APIView):
    permission_classes = [StaticTokenPermission]

    def put(self, request):
        id = request.query_params.get("id")
        req_data = request.query_params.get("is_verified")
        comment = request.query_params.get("comment")
        user_id = request.query_params.get("user_id")
        print("user_id",user_id)
        if not id and not req_data:
            return Response({"detail": "ID and Request Data is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            declaration = Declaration.objects.get(id=id)
        except Declaration.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        data = {"is_verified":req_data,"updated_by_id":user_id}
        serializer = UpdateDeclarationSerializer(declaration, data=data, partial=True)
        if serializer.is_valid():
            data = serializer.save()
            update_declaration_info_to_contract.delay((data.id))
            Declaration_log.objects.create(
                status = data.is_verified,
                declaration = data,
                comment = comment,
                created_by = True,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDeclarationLog(generics.ListAPIView):
    permission_classes = [StaticTokenPermission]
    serializer_class = ListDeclarationLogSerializer
    def get_queryset(self):
        id = self.request.query_params.get("id")
        return Declaration_log.objects.filter(declaration = id).order_by("-created_at")


def get_required_docs(request):
    hs_code_id = request.GET.get('hs_code')
    required_docs = RequiredDoc.objects.filter(hs_code_id=hs_code_id).values('id', 'name', 'format')
    return JsonResponse({'required_docs': list(required_docs)})

def get_document_data(request):
    doc_id = request.GET.get('doc_id')
    hs_code = request.GET.get('hs_code')
    item_id = request.GET.get('item_id')

    try:
        required_doc = RequiredDoc.objects.get(id=doc_id, hs_code=hs_code)
        document = Document.objects.get(required_doc=required_doc,item=item_id)
        response = FileResponse(document.file, as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
        return response
    except (Document.DoesNotExist, RequiredDoc.DoesNotExist):
        raise Http404("Document not found")

@require_POST
def delete_item(request, item_id):
    try:
        item = Items.objects.get(id=item_id)
        item.is_deleted = True
        item.save()
        return JsonResponse({'status': 'success'})
    except Items.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def Declaration_Logs_List(request,pk):
    declarations = Declaration.objects.get(id = pk)
    declaration_logs = Declaration_log.objects.filter(declaration = declarations).order_by('-created_at')
    return render(request, 'view_declaration_logs.html', {'logs': declaration_logs})

@csrf_exempt
def fetch_user_info(request):
    if request.method == 'POST':
        try:
            accounts = json.loads(request.body).get('accounts')
            if not accounts:
                return JsonResponse({'message': 'No accounts provided'}, status=400)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': settings.USER_API_KEY
            }
            EXTERNAL_API_URL = settings.IAM_URL + '/user/info/'

            data = {
                'accounts': accounts
            }

            response = requests.post(EXTERNAL_API_URL, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    user_data = result['data']['user']
                    request.session['wallet_address'] = user_data['wallet_address']
                    request.session['name'] = user_data['first_name']
                    request.session['id'] = user_data['id']
                    return JsonResponse({'status': 'success', 'user': user_data})
                else:
                    return JsonResponse({'status': 'error', 'message': result['message']}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'External API call failed'}, status=response.status_code)

        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Failed to decode JSON from response'}, status=500)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def delete_session(request):
    """
    This view deletes the user session from the website.
    Inputs: None (uses session data)
    Returns: JSON response with success or error message.
    """
    try:
        if 'wallet_address' in request.session:
            request.session.flush()
            return JsonResponse({"message": "Wallet address removed from session"}, status=200)
        else:
            return JsonResponse({"message": "No wallet address found in cookies"}, status=400)
    except Exception as e:
        return JsonResponse({"message": f"Failed to delete cookie: {str(e)}"}, status=500)
    

def connect_wallet(request):
    iam_base_url = settings.IAM_URL
    context = {
        "iam_base_url": iam_base_url 
    }
    return render(request, 'home.html',context)

class CreateDeclarationOpinion(APIView):

    renderer_classes = [renderers.JSONRenderer]
    def post(self, request: Request):

        # To use authentcation
        if not Authentication.is_authenticated(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        declaration_id = request.data.get("declarationId")
        department_ids = request.data.get("departmentIds")
        if not (declaration_id and department_ids):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                for department_id in department_ids:
                    opinion_object = Opinion(
                        declaration_id = declaration_id,
                        department_id = department_id,
                    )
                    opinion_object.save()
            return Response(
                {"result": "Opinion Data Successfully Saved"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response(data={"Result": e.args}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            return Response(
                data={"Result": e.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetDeclarationOpinionDataByDepartmentId(generics.ListAPIView):

    renderer_classes = [renderers.JSONRenderer]
    serializer_class = DelcarationListSerilaizer

    def get_queryset(self, declaration_ids):
            return Declaration.objects.filter(is_verified=0).order_by('-updated_at')
    
    def get(self, request: Request):

        if not Authentication.is_authenticated(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        department_id = request.GET.get("departmentId")

        if not department_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        opinion_data = Opinion.objects.filter(
            department_id=int(department_id)
        ).order_by("-created_at")

        try:
            if opinion_data:
                declaration_ids = []

                opinion_data_entries = []
                if opinion_data:
                    for opinion_obj in opinion_data:
                        entry = model_to_dict(opinion_obj)
                        entry['id'] = opinion_obj.id
                        opinion_data_entries.append(entry)
                        declaration_ids.append(opinion_obj.declaration_id)

                queryset = self.get_queryset(declaration_ids)
                serializer = self.get_serializer(queryset, many=True)

                return Response({"status": status.HTTP_200_OK,"declaration_data": serializer.data, "opinion_data":opinion_data_entries})
        except ValidationError as e:
            return Response(data={"Result": e.args}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            return Response(
                data={"Result": e.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateDeclarationOpinionData(APIView):

    renderer_classes = [renderers.JSONRenderer]

    def put(self, request: Request):
        if not Authentication.is_authenticated(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        opinion_id = request.data.get("opinionId")
        comment = request.data.get("comment","")
        opinion_status = request.data.get("status")
        employee_id = request.data.get("employeeId")
        employee_name = request.data.get("employeeName")

        if not (opinion_id and opinion_status and employee_id and employee_name):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        opinion_object = Opinion.objects.get(id=opinion_id)
        if not opinion_object:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            opinion_object.comment = comment
            opinion_object.status = int(opinion_status)
            opinion_object.employee_id = employee_id
            opinion_object.employee_name = employee_name

            with transaction.atomic():
                opinion_object.save()

            return Response(
                {"result": "Opinion Status Successfully Updated"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeclarationAssignUserIdView(APIView):

    renderer_classes = [renderers.JSONRenderer]

    def put(self, request: Request):
        if not Authentication.is_authenticated(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        declaration_id = request.data.get("warehouse_id")
        assign_user_id = request.data.get("assign_user_id")
        assign_user_name = request.data.get("assign_user_name")

        if not declaration_id or not assign_user_id or not assign_user_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        declaration_object = Declaration.objects.get(id=declaration_id)
        if not declaration_object:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            declaration_object.assign_user_id = assign_user_id
            declaration_object.assign_user_name = assign_user_name
            with transaction.atomic():
                declaration_object.save()

            return Response(
                {"result": "User Successfully Assigned"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
