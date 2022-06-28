from .models import Economic
from django import forms
from django.forms import TextInput

class EconomicForm(forms.ModelForm):
    class Meta:
        model = Economic
        fields = '__all__'
        widgets = {
                   'electricity_fixed_costs_per_year': TextInput(attrs={
                        'class': 'form-control',
                        'name': 'electricity_fixed_costs_per_year',
                        'id': 'electricity_fixed_costs_per_year',
                        'max': '1000',
                        'min': '10',
                        'value': '15',
                        'onchange':'rangeelectricity_fixed_costs_per_year.value = electricity_fixed_costs_per_year.value'

                   }),

                   'electricity_costs_per_kWh': TextInput(attrs={
                         'class': 'form-control',
                         'id': 'electricity_costs_per_kWh',
                         'name': 'electricity_costs_per_kWh',
                         'max': '1',
                         'min': '0.01',
                         'value': '0.05',
                         'onchange': 'rangeelectricity_costs_per_kWh.value = electricity_costs_per_kWh.value'
                   }),

                   'electricity_feed_in_tariff_for_photovoltaic': TextInput(attrs={
                         'class': 'form-control',
                         'id': 'electricity_feed_in_tariff_for_photovoltaic',
                         'name': 'electricity_feed_in_tariff_for_photovoltaic',
                         'max': '0.5',
                         'min': '0',
                         'value': '0.2',
                         'onchange': 'rangeelectricity_feed_in_tariff_for_photovoltaic.value = electricity_feed_in_tariff_for_photovoltaic.value'
                    }),
                    'electricity_feed_in_tariff_chp': TextInput(attrs={
                         'class': 'form-control',
                         'id': 'electricity_feed_in_tariff_chp',
                         'name': 'electricity_feed_in_tariff_chp',
                         'max': '0.5',
                         'min': '0',
                         'value': '0.2',
                         'onchange':'rangeelectricity_feed_in_tariff_chp.value =electricity_feed_in_tariff_chp.value'
                     }),

                    'gas_fixed_costs_per_year' : TextInput(attrs={
                         'class': 'form-control',
                         'id': 'gas_fixed_costs_per_year',
                         'name': 'gas_fixed_costs_per_year',
                         'max': '100',
                         'min': '5',
                         'value': '20',
                         'onchange':'rangegas_fixed_costs_per_year.value = gas_fixed_costs_per_year.value'
                     }),
                    'gas_costs_per_kwh': TextInput(attrs={
                         'class': 'form-control',
                         'id': 'gas_costs_per_kwh',
                         'name': 'gas_costs_per_kwh',
                         'max': '100',
                         'min': '5',
                         'value': '20',
                         'onchange':'rangegas_costs_per_kwh.value = gas_costs_per_kwh.value'
                     }),
                    'battery_costs_perkW_inverter_power': TextInput(attrs={
                        'class': 'form-control',
                        'id': 'battery_costs_perkW_inverter_power',
                        'name': 'battery_costs_perkW_inverter_power',
                        'max': '100',
                        'min': '5',
                        'value': '20',
                        'onchange': 'rangebattery_costs_perkW_inverter_power.value = battery_costs_perkW_inverter_power.value'

                   }),
                    'battery_costs_perkWh_capacity': TextInput(attrs={
                        'class': 'form-control',
                        'id': 'battery_costs_perkWh_capacity',
                        'name': 'battery_costs_perkWh_capacity',
                        'max': '100',
                        'min': '5',
                        'value': '20',
                        'onchange': 'rangebattery_costs_perkWh_capacity.value = battery_costs_perkWh_capacity.value'
                    }),
                    'battery_costs_for_maintenance_and_operations': TextInput(attrs={
                        'class': 'form-control',
                        'id': 'battery_costs_for_maintenance_and_operations',
                        'name': 'battery_costs_for_maintenance_and_operations',
                        'max': '100',
                        'min': '5',
                        'value': '15',
                        'onchange': 'rangebattery_costs_for_maintenance_and_operations.value = battery_costs_for_maintenance_and_operations.value'
                    }),
                    'battery_lifetime': TextInput(attrs={
                    'class': 'form-control',
                    'id': 'battery_lifetime',
                    'name': 'battery_lifetime',
                    'max': '100',
                    'min': '5',
                    'value': '15',
                    'onchange': 'rangebattery_lifetime.value =battery_lifetime.value'
                    }),
                    'hydrogen_costs_perkw_electrolyseur_power':TextInput(attrs={
                    'class': 'form-control',
                    'id': 'hydrogen_costs_perkw_electrolyseur_power',
                    'name': 'hydrogen_costs_perkw_electrolyseur_power',
                    'max': "10000000",
                    'value': "2500000",
                    'min': '5000',
                    'value': '15',
                    'onchange': 'rangehydrogen_costs_perkw_electrolyseur_power.value =hydrogen_costs_perkw_electrolyseur_power.value'

                    }),
                   'hydrogen_costs_perkw_fuel_cellpower': TextInput(attrs={
                       'class': 'form-control',
                       'id': 'hydrogen_costs_perkw_fuel_cellpower',
                       'name': 'hydrogen_costs_perkw_fuel_cellpower',
                       'max': "10000000",
                       'value': "2500000",
                       'min': '5000',
                       'value': '15',
                       'onchange': "rangehydrogen_costs_perkw_fuel_cellpower.value = hydrogen_costs_perkw_fuel_cellpower.value"

                   }),
                'rangehydrogen_costsperkWh_hydrogencapacity': TextInput(attrs={
                    'class': 'form-control',
                    'id': 'hydrogen_costsperkWh_hydrogencapacity',
                    'name': 'hydrogen_costsperkWh_hydrogencapacity',
                    'max': "10000000",
                    'value': "2500000",
                    'min': '5000',
                    'onchange': "rangehydrogen_costsperkWh_hydrogencapacity.value = hydrogen_costsperkWh_hydrogencapacity.value"
                    }),
                  'rangehydrogen_costs_for_maintenance_and_operations': TextInput(attrs={
                'class': 'form-control',
                'id': 'rangehydrogen_costs_for_maintenance_and_operations',
                'name': 'rangehydrogen_costs_for_maintenance_and_operations',
                'max': "10000000",
                'value': "2500000",
                'min': '5000',
                'onchange': "rangehydrogen_costs_for_maintenance_and_operations.value = hydrogen_costs_for_maintenance_and_operations.value"
                  }),
                 'hydrogen_lifetime': TextInput(attrs={
                'class': 'form-control',
                'id': 'hydrogen_lifetime',
                'name': 'hydrogen_lifetime',
                'max': "100",
                'min': '5',
                'value': '20',
                'onchange': 'rangehydrogen_lifetime.value = hydrogen_lifetime.value'
                 }),
                'hydrogen_interest_rate': TextInput(attrs={
                'class': 'form-control',
                'id': 'hydrogen_interest_rate',
                'name': 'hydrogen_interest_rate',
                'max': "100",
                'min': '5',
                'value': "20",
                'onchange': 'rangehydrogen_interest_rate.value = hydrogen_interest_rate.value'
                })

        }