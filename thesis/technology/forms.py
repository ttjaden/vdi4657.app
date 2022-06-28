from django import forms
from django.forms import TextInput
from django.forms import ModelForm
from .models import Tos, BuildingProfile

class BuildingProfileForm(forms.ModelForm):
    class Meta:
        model = BuildingProfile
        fields = '__all__'
        exclude = ['user','address']
        widgets = {
            'numofusers': TextInput(attrs={
                'class': "form-control",
                'name': 'numofusers',
                'id': 'numofusers',
                'max': '6',
                'min':'1',
                'value': "2",
                'onchange':'numofusersr.value = numofusers.value'
            }),
            
            'electricalenergyconsumptioni': TextInput(attrs={
                'class':'form-control',
                'id':'electricalenergyconsumptioni',
                'name':'electricalenergyconsumptioni',
                'max':'8000',
                'min':'2000',
                'value':'4000',
                'onchange':'electricalenergyconsumptionr.value = electricalenergyconsumptioni.value'
            }),
            
            'dhwenergyconsumptioni':TextInput(attrs={
                'class':'form-control',
                'id':'dhwenergyconsumptioni',
                'name':'dhwenergyconsumptioni',
                'max':'8000',
                'min':'2000',
                'value':'3000',
                'onchange':'dhwenergyconsumptionr.value = dhwenergyconsumptioni.value'
            }),

            'buildingsizei':TextInput(attrs={
                'class':'form-control',
                'id':'buildingsizei',
                'name':'buildingsizei',
                'max':'250',
                'min':'100',
                'value':'120',
                'onchange':'buildingsizer.value = buildingsizei.value'
            })
        }

class TosForm(forms.ModelForm):
    class Meta:
        model = Tos
        fields = '__all__'



