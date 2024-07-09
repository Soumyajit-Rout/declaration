from django.shortcuts import render,redirect
from .models import *
from .serializers import *
from .forms import DeclarationForm,ItemFormSet,ItemUpdateFormSet
from django.db import transaction
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from rest_framework import generics
from .permissions import StaticTokenPermission

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

        if not declaration_form.is_valid():
            print("Declaration Form Errors:", declaration_form.errors)
        if not item_formset.is_valid():
            print("Item Formset Errors:", item_formset.errors)

        if declaration_form.is_valid() and item_formset.is_valid():
         try:
            with transaction.atomic():
                declaration = declaration_form.save()
                item_formset.instance = declaration 
                item_formset.save()
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
            formset.save()
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
    description = data.get('description', '')
    description_data = re.findall(r'\b\w+\b', description)
    hs_codes_set = set()
    for word in description_data:
        matching_hs_codes = HsCode.objects.filter(
            keywords__icontains=word  
        )
        for hs_code in matching_hs_codes:
            if word in hs_code.keywords.split(','):
                hs_codes_set.add(hs_code)

    hs_codes = []
    for hs_code in hs_codes_set:
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
    queryset = Declaration.objects.filter(is_verified = 0)

"""
Basic api to retrieve the declarations based on id 
"""
class RetrieveDeclaration(generics.RetrieveAPIView):
    permission_classes = [StaticTokenPermission]
    serializer_class = DeclarationSerializer
    queryset = Declaration.objects.filter(is_verified = 0)
    lookup_field = "id"
    
"""
Basic api to update the declarations based on id 
"""
class UpdateDeclaration(generics.UpdateAPIView):
    permission_classes = [StaticTokenPermission]
    queryset = Declaration.objects.all()
    serializer_class = UpdateDeclarationSerializer
    lookup_field = "id"