from django.shortcuts import render

from plotly.offline import plot
from plotly.graph_objs import Scatter
from django.shortcuts import render,redirect
#from .forms import HeatpumpForm
from .forms import TosForm
from technology.forms import BuildingProfileForm
from .models import  Tos
from map.models import Address
from rest_framework.decorators import api_view
from rest_framework.response import Response
#from .serializers import ParameterSerializer
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import JsonResponse
import requests
import json


# Create your views here.
# Create your views here.
def index(request):
      return render(request, 'technology/index2.html')
def translate21 (request):
    return render(request, 'technology/page21.html')

def page2(request):

    return render(request,'page2.html' )

  
def page1(request):

    return render(request,'page1.html' )

def page21(request):

    return render(request,'page21.html' )
def tos(request):

    return render(request,'tos.html' )
def photo(request):

    return render(request,'photo.html' )

def pump(request):

    return render(request,'pump.html' )
def battery(request):

    return render(request,'battery.html' )
def comb(request):

    return render(request,'comb.html' )
def gas(request):

    return render(request,'gas.html' )
def electric(request):

    return render(request,'electric.html' )
def hydro(request):

    return render(request,'hydro.html' )

def test(request):

    return render(request,'test_plotly.html' )

def page3(request):
    return render(request,'technology/page3.html')








#-> new 
def create_building_profile(request, addr):
    form = BuildingProfileForm()
    technology = Tos.objects.all()
    context = {'Tos': technology, 'form':form }
    if request.method == 'POST':
        form = BuildingProfileForm(request.POST)
        if form.is_valid():
            building_profile = form.save(commit=False)
            building_profile.user = request.user            
            building_profile.address = Address.objects.get(id=addr)
            building_profile.building_type= request.POST.get('building_type')
            building_profile.save()
            return render(request, 'technology/tos.html', {'building_id': building_profile.id})

    return render(request, 'technology/create-building.html', context)
# <-


def tosform(request):
    form = TosForm(request.POST)

    if request.method == 'POST':
        Tos.objects.create(installedgenpower=request.POST.get("installedgenpower"),
                           azimut=request.POST.get("azimut"),
                           elevation=request.POST.get("elevation"),
                           ratedinverterpower=request.POST.get("ratedinverterpower"),
                           chpcombinedheatpower=request.POST.get("chpcombinedheatpower"),
                           chpoperationstrategy=request.POST.get("chpoperationstrategy"),
                           heatpumptechnology=request.POST.get("heatpumptechnology"),
                           heatpumpmodel=request.POST.get("heatpumpmodel"),
                           bsfeedinlimitation=request.POST.get("bsfeedinlimitation"),
                           bsusablecapacity=request.POST.get("bsusablecapacity"),
                           bsratedpower=request.POST.get("bsratedpower"),
                           hsusablecapacity=request.POST.get("hsusablecapacity"),
                           hsratedpower=request.POST.get("hsratedpower"),
                           elvehiclesdistance=request.POST.get("elvehiclesdistance"),
                           building_id=request.POST.get("building_id")
                           )


        #return render(request, 'economic/web_rest_test.html')
        #return redirect('economic:web-rest-test')
        return redirect('economic:dashboard')
        

    return render(request, 'economic/web_rest_test.html')
    #return redirect('economic:web-rest-test')
    #return redirect('economic:dashboard')



