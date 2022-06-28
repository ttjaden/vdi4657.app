from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import Economic
import requests
# Create your views here.




def dashboard(request):
    response = requests.get('http://127.0.0.2:8002/api/res-api/').json()
    toGraph = {
               'With_ElectricityFromGrid': response['WithElectricityStorage']['ElectricityFlowsTotal']['ElectricityFromGrid'],
               'With_TotalGasFlowFromGrid': response['WithElectricityStorage']['GasFlowsTotal']['TotalGasFlowFromGrid'],
               'WithOut_ElectricityFromGrid': response['WithOutElectricityStorage']['ElectricityFlowsTotal']['ElectricityFromGrid'],
               'WithOut_TotalGasFlowFromGrid': response['WithOutElectricityStorage']['GasFlowsTotal']['TotalGasFlowFromGrid'],
               'With_SelfConsumption': response['WithElectricityStorage']['TechnologicalKPIS']['SelfConsumption'],
               'WithOut_SelfConsumption': response['WithOutElectricityStorage']['TechnologicalKPIS']['SelfConsumption'],
               'WithOut_ElectrictyIntoGrid': response['WithOutElectricityStorage']['ElectricityFlowsTotal']['ElectrictyIntoGrid'],
               'With_ElectrictyIntoGrid': response['WithOutElectricityStorage']['ElectricityFlowsTotal']['ElectrictyIntoGrid'],
               'With_Autarky': response['WithElectricityStorage']['TechnologicalKPIS']['Autarky'],
               'WithOut_Autarky': response['WithOutElectricityStorage']['TechnologicalKPIS']['Autarky'],
               'With_GridSupplyCosts_ElectricityFromGrid': (response['WithElectricityStorage']['ElectricityFlowsTotal']['ElectricityFromGrid'])*0.31,
               'With_GridSupplyCosts_TotalGasFlowFromGrid': (response['WithElectricityStorage']['GasFlowsTotal']['TotalGasFlowFromGrid'])*0.064,
               'WithOut_GridSupplyCosts_ElectricityFromGrid': (response['WithOutElectricityStorage']['ElectricityFlowsTotal']['ElectricityFromGrid'])*0.31,
               'WithOut_GridSupplyCosts_TotalGasFlowFromGrid': (response['WithOutElectricityStorage']['GasFlowsTotal']['TotalGasFlowFromGrid'])*0.064,
               'WithOut_ElectricityIntoGridFromPV': (response['WithOutElectricityStorage']['ElectricityFlowsComponents']['ElectricityIntoGridFromPV'])*0.10,
               'WithOut_ElectricityIntoGridFromCHP': (response['WithOutElectricityStorage']['ElectricityFlowsComponents']['ElectricityIntoGridFromCHP'])*0.05,
               'With_ElectricityIntoGridFromPV': (response['WithElectricityStorage']['ElectricityFlowsComponents']['ElectricityIntoGridFromPV'])*0.10,
               'With_ElectricityIntoGridFromCHP': (response['WithElectricityStorage']['ElectricityFlowsComponents']['ElectricityIntoGridFromCHP'])*0.05,
    }
    print ( toGraph["With_GridSupplyCosts_TotalGasFlowFromGrid"])
    #return render(request, 'economic/web_rest_test.html', {'toGraph': toGraph})
    return render(request, 'economic/dashboard.html', {'toGraph': toGraph})


def economic(request):
    # form =EconomicForm()
    # context={'form': form }
    if request.method == 'POST':
        # form = EconomicForm(request.POST)
        # if form.is_valid():
        #  form.save()
        
        Economic.objects.create(electricity_fixed_costs_per_year = request.POST.get("electricity_fixed_costs_per_year"),
                                electricity_costs_per_kWh = request.POST.get("electricity_costs_per_kWh"), 
                                electricity_feed_in_tariff_chp = request.POST.get("electricity_feed_in_tariff_chp"), 
                                electricity_feed_in_tariff_for_photovoltaic = request.POST.get("electricity_feed_in_tariff_for_photovoltaic"), 
                                gas_fixed_costs_per_year = request.POST.get("gas_fixed_costs_per_year"),
                                gas_costs_per_kwh = request.POST.get("gas_costs_per_kwh"), 
                                battery_costs_perkW_inverter_power= request.POST.get("battery_costs_perkW_inverter_power"), 
                                battery_costs_perkWh_capacity= request.POST.get("battery_costs_perkWh_capacity"), 
                                battery_lifetime = request.POST.get("battery_lifetime"),
                                hydrogen_lifetime = request.POST.get("hydrogen_lifetime"), 
                                hydrogen_interest_rate=request.POST.get("hydrogen_interest_rate"), 
                                hydrogen_costs_perkw_fuel_cellpower = request.POST.get("hydrogen_costs_perkw_fuel_cellpower"),
                                hydrogen_costs_perkw_electrolyseur_power = request.POST.get("hydrogen_costs_perkw_electrolyseur_power"),
                                battery_costs_for_maintenance_and_operations = request.POST.get("battery_costs_for_maintenance_and_operations"),
                                hydrogen_costsperkWh_hydrogencapacity = request.POST.get("hydrogen_costsperkWh_hydrogencapacity"),
                                hydrogen_costs_for_maintenance_and_operations =request.POST.get("hydrogen_costs_for_maintenance_and_operations")
                                )
        
        #return redirect('economic:web-rest-test')
        return redirect('economic/dashboard.html')
  # return render(request, 'technology/web_rest_test.html', context)
    #return redirect('economic:web-rest-test')
    return redirect('economic/dashboard.html')




