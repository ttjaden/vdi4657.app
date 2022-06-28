from django.db import models
from technology.models import Tos

# Create your models here.



class Economic(models.Model):
    electricity_fixed_costs_per_year = models.FloatField(null=True)
    electricity_costs_per_kWh = models.FloatField(null=True)
    electricity_feed_in_tariff_chp = models.FloatField(null=True)
    electricity_feed_in_tariff_for_photovoltaic = models.FloatField(null=True)
    gas_fixed_costs_per_year = models.IntegerField(null=True)
    gas_costs_per_kwh = models.IntegerField(null=True)
    battery_costs_perkW_inverter_power= models.FloatField(null=True)
    battery_costs_perkWh_capacity= models.FloatField(null=True)
    battery_costs_for_maintenance_and_operations= models.FloatField(null=True)
    battery_lifetime = models.FloatField(null=True)
    hydrogen_costs_perkw_electrolyseur_power = models.FloatField(null=True)
    hydrogen_costs_perkw_fuel_cellpower = models.FloatField(null=True)
    hydrogen_costsperkWh_hydrogencapacity = models.FloatField(null=True)
    hydrogen_costs_for_maintenance_and_operations = models.FloatField(null=True)
    hydrogen_lifetime = models.FloatField(null=True)
    hydrogen_interest_rate = models.FloatField(null=True)
    tos = models.ForeignKey(Tos, on_delete=models.CASCADE, null=True)