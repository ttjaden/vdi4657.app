from django.db import models
from django.contrib.auth.models import User
import geocoder


# Create your models here.
class Address(models.Model):

      address = models.CharField(max_length=200, null=True)
      date = models.DateTimeField(auto_now_add=True)
      #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
      def __str__(self):
         return self.address
      
      def lat_lon(self):
            return (geocoder.osm(self.address).lat, geocoder.osm(self.address).lng)