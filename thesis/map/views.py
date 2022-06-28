from django.shortcuts import render, redirect
from .models import Address
from .forms import AddressForm
import folium
import geocoder

from .models import Address
from django.shortcuts import render




def map(request):
    address = Address.objects.all().last()
    address_id = address.id
    address=address.address
    
    if request.method =='POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('map:map')
        address = request.POST.get('address')
    else:
        form =AddressForm()

    location = geocoder.osm(address)
    lat = location.lat
    lng = location.lng
    country = location.country

    #Create Map Object
    # -> new
    if location is not None and location.current_result is not None:
        m = folium.Map(location=[lat, lng], zoom_start=6)
        folium.Marker(location=[lat, lng], tooltip='Click for more', popup=country).add_to(m)
    else: 
        m = folium.Map(location=[51.312711, 9.479746], zoom_start=6)
        folium.Marker([50.922423, 6.363912], tooltip='Click for more', popup='Jülich').add_to(m)
        address_id=1

       
    #Get HTML Representation of Map Object
    m = m._repr_html_()
    context = {
        'm': m,
        'form': form,
        'address':address_id
    }
    return render(request,'map/map.html', context )





# def map(request):
#     if request.method =='POST':
#         form = AddressForm(request.POST)
#         if form.is_valid():
#             form.save(commit=False)
#             form.user = request.user
#             form.save()
#             return redirect('map:map')
#     else:
#         form =AddressForm()
#     address = Address.objects.all().last().id
#     #address = request.POST.get('address')
#     location = geocoder.osm(address)
#     lat = location.lat
#     lng = location.lng
#     country = location.country

#     #Create Map Object
#     m = folium.Map(location=[51.312711, 9.479746], zoom_start=6)
#     folium.Marker([50.922423, 6.363912], tooltip='Click for more', popup='Jülich').add_to(m)
    
#     # -> new
#     if location is not None and location.current_result is not None:
#         folium.Marker(location=[lat, lng], tooltip='Click for more', popup=country).add_to(m)
#     # <-
    
#     #Get HTML Representation of Ma Object
#     m = m._repr_html_()
#     context = {
#         'm': m,
#         'form': form,
#         'address': address
#     }
#     return render(request,'map/map.html', context)

