import os
import csv
import glob
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse

# --- УНИВЕРСАЛЬНЫЙ ЧИТАТЕЛЬ ---
def read_latest_data():
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    all_files = glob.glob(os.path.join(data_dir, "*.*"))
    if not all_files: return []
    
    # Берем самый свежий файл по дате изменения
    latest_file = max(all_files, key=os.path.getmtime)
    
    try:
        # Читаем Excel
        if latest_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(latest_file)
        # Читаем CSV
        else:
            with open(latest_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                sample = f.read(2048)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t'])
                df = pd.read_csv(f, dialect=dialect)
        
        # Приводим названия колонок к стандарту
        df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

# --- ЗАГРУЗКА ---
@login_required
def upload_sales_data(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        uploaded_file = request.FILES["excel_file"]
        data_dir = os.path.join(settings.BASE_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)

        # Удаляем старые файлы, чтобы дашборд показывал только актуальный
        for f in glob.glob(os.path.join(data_dir, "*.*")):
            os.remove(f)

        path = os.path.join(data_dir, uploaded_file.name)
        with open(path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        messages.success(request, "Файл загружен и активирован.")
    return redirect("stat-index")

# --- ДАШБОРД ---
@login_required
def index(request):
    orders_list = read_latest_data()
    
    sum_outcome, total_orders, total_refounds, sales_count = 0, 0, 0, 0
    category_sps, pie_sps, date_sps, profit_sps = {}, {}, {}, {}

    for order in orders_list:
        try:
            # Ищем цену в разных вариациях названий колонок
            out_price = int(float(order.get("outcome_price") or order.get("outcome") or 0))
            inc_price = int(float(order.get("income_price") or order.get("income") or 0))
        except (ValueError, TypeError): continue
            
        sum_outcome += out_price
        total_orders += 1
        
        status = str(order.get("order_status", "")).lower()
        if status in ["paid", "completed", "done"]:
            sales_count += 1
        if status == "cancelled":
            total_refounds += 1
        
        cat = str(order.get("category", "Other"))
        channel = str(order.get("sales_channel", "Website"))
        date = str(order.get("date", "00-01-00")).replace(".", "-")
        
        category_sps[cat] = category_sps.get(cat, 0) + out_price
        
        if "-" in date:
            parts = date.split("-")
            month = parts[1] if len(parts) > 1 else "01"
            date_sps[month] = date_sps.get(month, 0) + out_price
            profit_sps[month] = profit_sps.get(month, 0) + (out_price - inc_price)
        
        pie_sps[channel] = pie_sps.get(channel, 0) + out_price

    total_visitors = len(orders_list)
    conversion = (sales_count / total_visitors * 100) if total_visitors > 0 else 0

    context = {
        'total_revenue': sum_outcome,
        'orders': total_orders,
        'refounds': total_refounds,
        'conversion_rate': round(conversion, 2),
        'latest_orders': orders_list[-4:],
        'months_': sorted(list(date_sps.keys())),
        'revenue_data_': date_sps,
        'profit_data_': profit_sps,
        'labels_sales_channel': list(pie_sps.keys()),
        'data_sales_channel': list(pie_sps.values()),
        'labels_category': list(category_sps.keys()),
        'data_category': list(category_sps.values()),
    }
    return render(request, 'tut_stat/index.html', context)
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
        writer.writerow(orders_list[0].keys())
        for order in orders_list:
            writer.writerow(order.values())
    return response

class StatIndexView(UserPassesTestMixin, TemplateView):
    template_name = 'tut_stat/index.html'
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser