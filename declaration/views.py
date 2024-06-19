from django.shortcuts import render,redirect
from .models import *
from .forms import DeclarationForm,ItemFormSet,ItemUpdateFormSet
from django.db import transaction
from django.db import transaction


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
            return redirect('create_declaration')
         
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


