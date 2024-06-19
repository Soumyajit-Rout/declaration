from django.urls import path
from . import views

urlpatterns = [
     path('create-declaration/', views.create_declaration, name='create_declaration'),
     path('', views.declaration_list, name='view_declaration'),
     path('update/<uuid:pk>/', views.update_declaration, name='update_declaration'),
     path('delete/<uuid:pk>/', views.delete_declaration, name='delete_declaration'),
]
