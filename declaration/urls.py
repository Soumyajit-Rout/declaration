from django.urls import path
from . import views
from .views import *

urlpatterns = [
     path('create-declaration/',create_declaration, name='create_declaration'),
     path('', declaration_list, name='view_declaration'),
     path('update/<uuid:pk>/', update_declaration, name='update_declaration'),
     path('delete/<uuid:pk>/', delete_declaration, name='delete_declaration'),
     path('search-hscode/', search_hscode, name='search_hscode'),
     path('api/declaration/verification/getDeclaration',ListDeclarations.as_view(),name='list_declaration'),
     path('api/declaration/verification/getDeclarationById/<uuid:id>',RetrieveDeclaration.as_view(),name='retrieve_declaration'),
     path('api/declaration/verification/updateDeclaration/<uuid:id>',UpdateDeclaration.as_view(),name='retrieve_declaration')


]
