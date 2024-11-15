from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('create-declaration/',create_declaration, name='create_declaration'),
     path('view-declaration/', declaration_list, name='view_declaration'),
     path('update/<uuid:pk>/', update_declaration, name='update_declaration'),
     path('retrieve/<uuid:pk>/', list_declaration, name='list_declaration'),
     path('delete/<uuid:pk>/', delete_declaration, name='delete_declaration'),
     path('search-hscode/', search_hscode, name='search_hscode'),
     path('update-search-hscode/<uuid:pk>/', update_search_hscode, name='update_search_hscode'),
     path('list-items/<uuid:pk>/', list_items, name='list_items'),
     path('retrive-items/<uuid:pk>/', retrieve_items, name='retrieve_items'),


     
     path('get-required-docs/', get_required_docs, name='get_required_docs'),
     path('get-document-data/', get_document_data, name='get-document-data'),
     path('delete-item/<uuid:item_id>/',delete_item,name='delete_item'),
     path('view-logs/<uuid:pk>/',Declaration_Logs_List,name='view-logs'),
     path('fetch/user/',fetch_user_info,name='fetch_user_info'),
     path('delete_session/',delete_session,name='delete_session'),
     path('',connect_wallet,name='onboard'),

     # APIs for Internal Communication
     # Verification
     path('api/DeclarationRegistration/verification/getDeclarationRegistrationData',ListDeclarations.as_view(),name='list_declaration'),
     path('api/DeclarationRegistration/verification/getDeclarationRegistrationDatabyId',RetrieveDeclaration.as_view(),name='retrieve_declaration'),
     path('api/DeclarationRegistration/verification/updateDeclarationRegistrationData',UpdateDeclaration.as_view(),name='retrieve_declaration'),
     path('api/DeclarationRegistration/verification/listDeclarationLogData',ListDeclarationLog.as_view(),name='retrieve_declaration'),
     path('api/DeclarationRegistration/verification/assignUserId', views.DeclarationAssignUserIdView.as_view()),
     
     # Opinion
     path('api/DeclarationOpinion/createDeclarationOpinion', views.CreateDeclarationOpinion.as_view(),name='create_declaration_opinion'),
     path('api/DeclarationOpinion/getDeclarationOpinionDataByDepartmentId', views.GetDeclarationOpinionDataByDepartmentId.as_view(),name='get_declaration_opinion'),
     path('api/DeclarationOpinion/updateDeclarationOpinionData', views.UpdateDeclarationOpinionData.as_view(),name='update_declaration_opinion'),

     #General
     path('api/Declaration/getDeclarationItem', views.GetItemsByDeclarationId.as_view(),name='get_item'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)