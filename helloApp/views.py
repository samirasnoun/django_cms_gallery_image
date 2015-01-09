from django.shortcuts import render
from django.views import generic

# Create your views here.

class Hello(generic.TemplateView):
    template_name = 'hello_plugin.html'
    
    

    
