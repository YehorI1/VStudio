import os
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def upload_sales_data(request):
    if request.method != "POST":
        return redirect("stat-index")

    uploaded_file = request.FILES.get("excel_file")
    if not uploaded_file:
        messages.error(request, "Файл не был выбран!")
        return redirect("stat-index")

    # Проверка расширения
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in {".csv", ".xlsx", ".xls"}:
        messages.error(request, "Неверный формат файла.")
        return redirect("stat-index")

    # Путь к папке data
    data_dir = os.path.join(settings.BASE_DIR, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Сохраняем всегда под одним именем для простоты чтения
    target_path = os.path.join(data_dir, "all_orders.csv")

    # Сохранение через бинарный режим
    try:
        with open(target_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        messages.success(request, "Файл успешно обновлен!")
    except Exception as e:
        messages.error(request, f"Ошибка при сохранении файла: {e}")
        
    return redirect("stat-index")