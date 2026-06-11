from django.contrib import admin
from django.urls import path
from tut_interface.views import HomeIndexView
from tut_office.views import OfficeIndexView
from tut_autoris.views import login_view, logout_view, register_view
from tut_stat import views as stat_views  # Импортируем модуль views из stat

urlpatterns = [
    path("", HomeIndexView.as_view(), name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('admin/logout/', logout_view, name='admin-logout'),
    path('stat/', stat_views.index, name='stat-index'),
    path('office/', OfficeIndexView.as_view(), name='office-index'),
    path('admin/', admin.site.urls),
    path('stat/upload/', stat_views.upload_sales_data, name='upload_sales_data'),
    path('export/', stat_views.export_csv, name='export_csv'), # Работает через stat_views!
]