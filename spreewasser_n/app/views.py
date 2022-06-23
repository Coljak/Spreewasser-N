from django.shortcuts import render
from requests import request
from . import forms


# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def home(request):
    return render(request, 'app/home.html')

def login(request):
    return render(request, 'app/login.html')

def form_sidebar(request):
    form = forms.FormSidebar()

    if request.method == 'POST':
        form = forms.FormSidebar(request.POST)

        if form.is_valid():
            print('data has come in...')
            print(form.cleaned_data['name'])
            print(form.cleaned_data['email'])
            print(form.cleaned_data['text'])
    return render(request, 'app/form_sidebar.html', {'form': form})

def userinfo(request):
    return render(request, 'app/userinfo.html')

def userproject(request):
    return render(request, 'app/userproject.html')

def map(request):
    return render(request, 'app/map.html')

