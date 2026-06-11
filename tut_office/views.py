from django.shortcuts import render
from django.views.generic import TemplateView

class OfficeIndexView(TemplateView):
    template_name = 'tut_office/index.html'
