from django.shortcuts import render
from django.http import JsonResponse
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from technology.models import Tos, BuildingProfile
from map.models import Address
from .serializers import AddressSerializer, TosSerializer, BuildingProfileSerializer
#from .serializers import ParameterSerializer
#from thesis.models import Parameters

# Create your views here.

@api_view(['GET'])
def buildingProfileList(request):
    list_building = BuildingProfile.objects.all()
    serializer = BuildingProfileSerializer(list_building, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tosList(request):
    list_tos = Tos.objects.all()
    serializer = TosSerializer(list_tos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def addressList(request):
    list_address = Address.objects.all()
    serializer = AddressSerializer(list_address, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def allList(request):
    list_search= Address.objects.all()
    list_buildingProfile = BuildingProfile.objects.all()
    list_tos = Tos.objects.all()

    data = {
        'buildingProfile':BuildingProfileSerializer(list_buildingProfile, many=True).data,
        'tos': TosSerializer(list_tos, many=True).data,
        'search':AddressSerializer(list_search, many=True).data,
    }

    #return Response(json.dumps(data))
    return Response(data)
@api_view(['GET'])
def allListUser(request, user_id):
    
    user = get_object_or_404(User, id=user_id)
    # list_address= Address.objects.filter(user=user)
    list_buildingProfile = BuildingProfile.objects.filter(user=user)
    list_tos = Tos.objects.filter(building__user=user)

    data = {
        'buildingProfile': BuildingProfileSerializer(list_buildingProfile, many=True).data,
        'tos': TosSerializer(list_tos, many=True).data,
        #'address':AddressSerializer(list_address, many=True).data,
    }

    #return Response(json.dumps(data))
    return Response(data)


@api_view(['GET'])
def apiOverview(request):
    api_urls = {
    'list-tos':'list-tos',
    'list-buildingProfile':'list-buildingProfile/',
    'list-address':'list-address',
    'list-all':'list-all',
    'list-all-user':'list-all<int:user_id>',
    }
    return Response(api_urls)

@api_view(['GET'])
def apiResults(request):

    res_data = {"SimulationParameters": {"year": 2019,
                                     "seconds_per_timestep": 900,
                                     "method": "full_year"},
            "WithElectricityStorage":{"TechnologicalKPIS": {"Autarky": 500, #to grap
                                       "SelfConsumption": 400,
                                       "UtilisationHours": 1000},
                 "ElectricityFlowsTotal": {"ElectricityFromGrid": 1100, #to graph
                                           "ElectrictyIntoGrid": 1300,
                                           "MaximimumPowerOfGrid": 100,
                                           "ElectricityLostCurtailment": 10},
                 "ElectricityFlowsComponents": {"ElectricityFromGridIntoBattery": 500,
                                                "ElectricityFromGridIntoHeatPump": 500,
                                                "ElectricityFromGridIntoHouse": 9000,
                                                "ElectricityIntoGridFromPV": 500,
                                                "ElectricityIntoGridFromCHP": 500
                                                },
                 # to graph
                 "GasFlowsTotal": {"TotalGasFlowFromGrid": 1200, #to graph
                                   "TotalGasFromGridIntoCHP": 1000,
                                   "TotalGasFromGridIntoGasBoiler": 1000},
                 },
            "WithOutElectricityStorage":
                {"TechnologicalKPIS": {"Autarky": 400, # to graph
                                       "SelfConsumption": 300,
                                       "UtilisationHours": 1000},
                 "ElectricityFlowsTotal": {"ElectricityFromGrid": 1200, #to graph
                                           "ElectrictyIntoGrid": 1100,
                                           "MaximimumPowerOfGrid": 100,
                                           "ElectricityLostCurtailment": 10},
                 "ElectricityFlowsComponents": {"ElectricityFromGridIntoBattery": 500,
                                                "ElectricityFromGridIntoHeatPump": 500,
                                                "ElectricityFromGridIntoHouse": 9000,
                                                "ElectricityIntoGridFromPV": 500,
                                                "ElectricityIntoGridFromCHP": 500
                                                },
                 "GasFlowsTotal": {"TotalGasFlowFromGrid": 1000, #to graph
                                   "TotalGasFromGridIntoCHP": 1000,
                                   "TotalGasFromGridIntoGasBoiler": 1000},
                 }
            }


    return Response(res_data)