import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .views import read_latest_data  # Импортируем функцию чтения из основного views

@login_required
def export_csv(request):
    orders_list = read_latest_data()
    
    if not orders_list:
        messages.error(request, "Нет данных для экспорта!")
        return redirect("stat-index")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

    writer = csv.writer(response)
    
    if orders_list:
        # Записываем заголовки
        writer.writerow(orders_list[0].keys())
        # Записываем данные
        for order in orders_list:
            writer.writerow(order.values())
        
    return response