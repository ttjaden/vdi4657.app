from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import MyUserCreationForm
# Create your views here.
def loginPage(request):
    page = 'login'
    # if request.user.is_authenticated:
    #     return redirect ('technology:thesis-index')

    if request.method == 'POST':
        username_try = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username_try)
        except User.DoesNotExist:
            # messages.error(request,"User doesn't exist")
            HttpResponse("User doesn't exist")
        
        user = authenticate (request, username=username_try, password=password)
        if user is not None:
            login(request, user)
            return redirect ('technology:thesis-index')
        else:
            # messages.error(request,"Username or password incorrect")
            HttpResponse("Username or password incorrect")

    context = {'page':page }
    return render (request, 'user_manage/login_register.html', context)


def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # to clean up the data and have accessto to the user object
            user.username = user.username.lower()
            user.save()
            login (request, user)
            return redirect ('technology:thesis-index')
        else:
            # messages.error(request, 'An error occurred while creating a new user')
            HttpResponse ('An error occurred while creating a new user')


    context = {'form':form,
                'page':page
                }
    return render (request, 'user_manage/login_register.html',context)

def logoutUser(request):
    logout (request)
    return redirect ('technology:thesis-index')
