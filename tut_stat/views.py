import os
import csv
import glob
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

# --- УНИВЕРСАЛЬНЫЙ ЧИТАТЕЛЬ (читает любой CSV в папке) ---
def read_latest_csv():
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not all_files: return []
    
    # Берем самый последний загруженный файл
    latest_file = max(all_files, key=os.path.getmtime)
    
    data = []
    with open(latest_file, mode='r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read(2048)
        delimiter = ';' if ';' in content else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            # Нормализация ключей
            clean_row = {str(k).lower().strip().replace(" ", "_"): v.strip() 
                         for k, v in row.items() if k is not None}
            data.append(clean_row)
    return data

@login_required
def upload_sales_data(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        uploaded_file = request.FILES["excel_file"]
        data_dir = os.path.join(settings.BASE_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)
        # Сохраняем под именем файла пользователя
        path = os.path.join(data_dir, uploaded_file.name)
        with open(path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        messages.success(request, f"Файл {uploaded_file.name} загружен!")
    return redirect("stat-index")

@login_required
def index(request):
    orders_list = read_latest_csv()
    
    sum_outcome, total_orders, total_refounds = 0, 0, 0
    category_sps, pie_sps, date_sps, profit_sps = {}, {}, {}, {}
    
    # Считаем конверсию (если есть статус 'converted' или 'paid' и клики/показы)
    # Предположим: total_orders - это продажи, а общее число строк - это посетители
    total_visitors = len(orders_list)
    sales_count = 0

    for order in orders_list:
        try:
            out_price = int(float(order.get("outcome_price", 0) or 0))
            inc_price = int(float(order.get("income_price", 0) or 0))
        except ValueError: continue
            
        sum_outcome += out_price
        total_orders += 1
        if order.get("order_status", "").lower() in ["paid", "completed"]:
            sales_count += 1
        
        cat = order.get("category", "Other")
        channel = order.get("sales_channel", "Website")
        date = order.get("date", "00-01-00").replace(".", "-")
        
        if order.get("order_status", "").lower() == "cancelled":
            total_refounds += 1
        
        category_sps[cat] = category_sps.get(cat, 0) + out_price
        if "-" in date:
            month = date.split("-")[1]
            date_sps[month] = date_sps.get(month, 0) + out_price
            profit_sps[month] = profit_sps.get(month, 0) + (out_price - inc_price)
        pie_sps[channel] = pie_sps.get(channel, 0) + out_price

    # Расчет конверсии
    conversion_rate = (sales_count / total_visitors * 100) if total_visitors > 0 else 0

    context = {
        'total_revenue': sum_outcome,
        'orders': total_orders,
        'refounds': total_refounds,
        'conversion_rate': round(conversion_rate, 2), # Добавляем в контекст
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

class StatIndexView(UserPassesTestMixin, TemplateView):
    template_name = 'tut_stat/index.html'
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser