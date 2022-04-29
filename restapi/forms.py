from dataclasses import field
import imp
from random import choice, choices
from warnings import filters
from django import forms
from .models import ValuationAPI
import json


with open("complex.json", "r", encoding='utf-8') as f:
    complex_dict = json.load(f)
adr=[]
for complex in complex_dict.keys():
    adr.append((complex_dict[complex], complex))

cit = (('city_Астана', 'Астана (Нур-Султан)'))

reg = (('region_Есильский р-н', "Есильский"), ('region_Алматы р-н', 'Aлматы'),
( 'region_Сарыарка р-н', "Сарыарка"), (' ', "Байконур"))

ren = (('renovation_хорошее', 'хорошее'), (' ', "требует ремонта"),
('renovation_черновая отделка', 'черновая отделка'))

toi = (('toilet_раздельный', 'раздельный'),('toilet_совмещенный', 'совмещенный'),
(' ', '2 с/у и более'))

bal = ((' ', ' '), ('balcony_балкон', 'балкон'), ('balcony_лоджия', 'лоджия'),
 ('balcony_несколько балконов или лоджий', 'несколько балконов или лоджий'))

bt = (('building_type_монолитный', 'монолитный'), ('building_type_панельный', 'панельный'), 
('building_type_кирпичный', 'кирпичный'), (' ', 'иное'))

cc = (('complex_class_Экономкласс', 'Эконом-класс'), ('complex_class_Комфорт-класс', 'Комфорт-класс'),
('complex_class_Бизнес-класс', 'Бизнес-класс'), (' ', 'Элит'))


security_one_hot = (
    (' ', ' '),

    ('security_домофон', 'домофон'),

    ('security_видеонаблюдение', 'видеонаблюдение'),

    ('security_видеодомофон', 'видеодомофон'),

    ('security_охрана', 'охрана'),

    ('security_сигнализация', 'сигнализация'),

    ('security_консьерж', 'консьерж'),

)

class ValuationAPIForm(forms.ModelForm):
    class Meta:
        model = ValuationAPI
        fields = '__all__'
    rooms = forms.IntegerField()
    ceiling = forms.FloatField()
    building_year = forms.IntegerField()
    floor = forms.IntegerField()
    total_floors = forms.IntegerField()
    area = forms.FloatField()
    address = forms.CharField(max_length=200)
    region = forms.ChoiceField(choices=reg)
    renovation = forms.ChoiceField(choices=ren)
    toilet = forms.ChoiceField(choices=toi)
    balcony = forms.ChoiceField(choices=bal)
    building_type = forms.ChoiceField(choices=bt)
    complex_class = forms.ChoiceField(choices=cc)
    #complex_class = forms.CharField(max_length=200)
    security = forms.ChoiceField(choices=security_one_hot)
    #complex = forms.ChoiceField(choices=tuple(adr))  #выпадающий список должен быть только в forms.py 
