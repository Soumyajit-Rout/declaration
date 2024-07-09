from rest_framework import serializers
from .models import *



class DeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = '__all__'

class UpdateDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ["is_verified"]