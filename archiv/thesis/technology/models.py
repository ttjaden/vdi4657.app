from django.db import models
from django.contrib.auth.models import User
from map.models import Address
# from django.contrib.auth.models import AbstractUser

class BuildingProfile(models.Model):
        building_type = models.CharField(max_length=20)
        numofusers = models.IntegerField(null=True)
        electricalenergyconsumptioni = models.IntegerField(null=True)
        dhwenergyconsumptioni = models.IntegerField(null=True)
        buildingsizei = models.IntegerField(null=True)
        address =  models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
        user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
        


class Tos(models.Model):
    installedgenpower = models.IntegerField(null=True)
    azimut = models.IntegerField(null=True)
    elevation = models.IntegerField(null=True)
    ratedinverterpower = models.IntegerField(null=True)
    chpcombinedheatpower = models.CharField(max_length=20, null=True)
    chpoperationstrategy = models.CharField(max_length=20, null=True)
    heatpumptechnology = models.CharField(max_length=20, null=True)
    #thermalpowerneeded = models.CharField(max_length=20, null=True)
    heatpumpmodel=models.CharField(max_length=20, null=True)
    bsfeedinlimitation=models.FloatField(null=True)
    bsusablecapacity=models.FloatField(null=True)
    bsratedpower=models.FloatField(null=True)
    hsusablecapacity=models.IntegerField(null=True)
    hsratedpower=models.IntegerField(null=True)
    elvehiclesdistance= models.IntegerField(null=True)
    building = models.ForeignKey(BuildingProfile, on_delete=models.CASCADE, null=True)
  

# class User (AbstractUser): 


