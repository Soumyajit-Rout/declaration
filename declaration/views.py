from django.shortcuts import render,redirect
from .models import *
from .serializers import *
from .forms import DeclarationForm,ItemFormSet,ItemUpdateFormSet,DocumentFormSet
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
            print("i anm in")
            try:
                with transaction.atomic():
                    declaration = declaration_form.save()
                    item_formset.instance = declaration
                    items = item_formset.save()
                    
                    for item in items:
                        hs_code = item.hs_code
                        if hs_code:
                            print("in1")
                            required_docs = RequiredDoc.objects.filter(hs_code=hs_code)
                            for req_doc in required_docs:
                                file_field_name = f'documents_{req_doc.id}'
                                if file_field_name in request.FILES:
                                    print("in2")

                                    Document.objects.create(
                                        item=item,
                                        file=request.FILES[file_field_name],
                                        required_doc = req_doc
                                    )

                return redirect('view_declaration')
            except Exception as e:
                print(e)
                declaration_form.add_error(None, 'An error occurred while saving items.')
    else:
        declaration_form = DeclarationForm()
        item_formset = ItemFormSet()
        # document_formset = DocumentFormSet()

    return render(request, 'create_declaration.html', {
        'form': declaration_form,
        'item_formset': item_formset,
    })
"""
This function is to display the declaration objects it is a normal list function and
renders the view_declaration.html page
"""
def declaration_list(request):
    declarations = Declaration.objects.all()
    return render(request, 'view_declaration.html', {'declarations': declarations})

"""
This function is to update the declaration form as well as the item objects,here the 
function expects an id of the declaration object,once the updation is completed,the 
page gets redirected to view_declaration page and here the page which is being rendered is
the update_declaration.html
"""
def update_declaration(request, pk):
    declaration = Declaration.objects.get(id=pk)

    if request.method == 'POST':
        form = DeclarationForm(request.POST, instance=declaration)
        formset = ItemUpdateFormSet(request.POST, instance=declaration)
        if not form.is_valid():
            print("Declaration Form Errors:", form.errors)
        if not formset.is_valid():
            print("Item Formset Errors:", formset.errors)

        if form.is_valid() and formset.is_valid():
            form.save()
            items = formset.save()
            print("items",items)
            for item in items:
                print("in1")
                hs_code = item.hs_code
                required_doc = RequiredDoc.objects.filter(hs_code=hs_code)
                for doc in required_doc:
                    print("Processing doc:", doc.id)

                    file_field_name = f'documents_{doc.id}_{item.id}'
                    if file_field_name in request.FILES:
                        print("File field found:", file_field_name)
                        uploaded_file = request.FILES[file_field_name]
                        print("Uploaded file:", uploaded_file.name)

                        if Document.objects.get(required_doc=doc, item=item):
                            print("Document exists, updating...")
                            Document.objects.filter(required_doc=doc, item=item).update(
                                item=item,
                                required_doc=doc,
                                file=uploaded_file
                            )
                        else:
                            print("Creating new document...")
                            Document.objects.create(
                                item=item,
                                required_doc=doc,
                                file=uploaded_file
                            )
            if not items:
                items = Items.objects.filter(declaration=declaration)
                print(request.FILES)
                for item in items:
                    hs_code = item.hs_code
                    required_docs = RequiredDoc.objects.filter(hs_code=hs_code)
                    for doc in required_docs:
                        file_field_name = f'documents_{doc.id}_{item.id}'
                        if file_field_name in request.FILES:
                            Document.objects.update(
                                required_doc=doc, item=item,
                                file =request.FILES[file_field_name]
                            )

            return redirect('view_declaration')
    else:
        form = DeclarationForm(instance=declaration)
        formset = ItemUpdateFormSet(instance=declaration)

    return render(request, 'update_declaration.html', {'form': form,'item_formset': formset,})

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

"""
Basic api to list the declarations 
"""
class ListDeclarations(generics.ListAPIView):
    permission_classes = [StaticTokenPermission]
    serializer_class = DeclarationSerializer

    def get_queryset(self):
        return Declaration.objects.filter(is_verified=0)

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
        except Declaration.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeclarationSerializer(declaration)
        return Response({"status":status.HTTP_200_OK,"registration_data":serializer.data})
    
"""
Basic api to update the declarations based on id 
"""
class UpdateDeclaration(APIView):
    permission_classes = [StaticTokenPermission]

    def put(self, request):
        id = request.query_params.get("id")
        req_data = request.query_params.get("is_verified")
        comment = request.query_params.get("comment")
        if not id and not req_data:
            return Response({"detail": "ID and Request Data is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            declaration = Declaration.objects.get(id=id)
        except Declaration.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        data = {"is_verified":req_data}
        serializer = UpdateDeclarationSerializer(declaration, data=data, partial=True)
        if serializer.is_valid():
            data = serializer.save()
            print("data",data)
            Declaration_log.objects.create(
                status = data.is_verified,
                declaration = data,
                comment = comment,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDeclarationLog(generics.ListAPIView):
    permission_classes = [StaticTokenPermission]
    serializer_class = ListDeclarationLogSerializer
    def get_queryset(self):
        id = self.request.query_params.get("id")
        return Declaration_log.objects.filter(declaration = id)


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
