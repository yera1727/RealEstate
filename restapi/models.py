from audioop import add
from distutils.command.build import build
from django.db import models
import json

# Create your models here.
class ValuationAPI(models.Model):  
    rooms = models.IntegerField()
    ceiling = models.FloatField()
    building_year = models.IntegerField()
    floor = models.IntegerField()
    total_floors = models.IntegerField()
    area = models.FloatField()
    address = models.CharField(max_length=200)
    '''complex = models.CharField(max_length=1, choices=tuple(adr), default=1)''' #выпадающий список должен быть только в forms.py 
    region = models.CharField(max_length=200)    
    renovation = models.CharField(max_length=200)
    toilet = models.CharField(max_length=200)
    balcony = models.CharField(max_length=200)
    building_type = models.CharField(max_length=200)
    complex_class = models.CharField(max_length=200)
    #complex = models.CharField(max_length=300)
    security = models.CharField(max_length=300)
    


'''
    def __str__(self):
        return self.complex, self.region
'''
