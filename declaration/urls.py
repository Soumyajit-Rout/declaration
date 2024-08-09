from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('create-declaration/',create_declaration, name='create_declaration'),
     path('', declaration_list, name='view_declaration'),
     path('update/<uuid:pk>/', update_declaration, name='update_declaration'),
     path('retrieve/<uuid:pk>/', list_declaration, name='list_declaration'),
     path('delete/<uuid:pk>/', delete_declaration, name='delete_declaration'),
     path('search-hscode/', search_hscode, name='search_hscode'),
     path('update-search-hscode/<uuid:pk>/', update_search_hscode, name='update_search_hscode'),
     path('api/DeclarationRegistration/verification/getDeclarationRegistrationData',ListDeclarations.as_view(),name='list_declaration'),
     path('api/DeclarationRegistration/verification/getDeclarationRegistrationDatabyId',RetrieveDeclaration.as_view(),name='retrieve_declaration'),
     path('api/DeclarationRegistration/verification/updateDeclarationRegistrationData',UpdateDeclaration.as_view(),name='retrieve_declaration'),
     path('api/DeclarationRegistration/verification/listDeclarationLogData',ListDeclarationLog.as_view(),name='retrieve_declaration'),
     path('get-required-docs/', get_required_docs, name='get_required_docs'),
     path('get-document-data/', get_document_data, name='get-document-data'),
     path('delete-item/<uuid:item_id>/',delete_item,name='delete_item'),
     path('view-logs/<uuid:pk>/',Declaration_Logs_List,name='view-logs'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)