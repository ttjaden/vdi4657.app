from django.contrib import admin

from .models import Tos, BuildingProfile

class EntryAdmin(admin.ModelAdmin):
    list_display = ('technology', 'model')
    list_filter = ['model']



admin.site.register(Tos)
admin.site.register(BuildingProfile)



admin.site.site_header = "Jülich Dashboard"

