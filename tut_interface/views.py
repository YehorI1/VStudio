from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# class HomeIndexView(LoginRequiredMixin, TemplateView):
class HomeIndexView(TemplateView):
    template_name = 'index.html'
    # login_url = '/autoris/'
    # redirect_field_name = None
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['user'] = self.request.user
    #     return context
