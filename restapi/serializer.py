from dataclasses import fields
from operator import mod
from rest_framework import serializers
from .models import ValuationAPI

class ValuationSerializers(serializers.ModelSerializer):
    class meta:
        model=ValuationAPI
        fields='__all__'
    