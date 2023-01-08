from django.urls import path
from rr_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('master/', views.master, name='master'),
    path('crud_operation/', views.crud_operation, name='crud_operation'),
    path('tenant_bill/', views.tenant_bill, name='tenant_bill'),
    path('tenant_bill_crud/', views.tenant_bill_crud, name='tenant_bill_crud'),
    path('name_room_list/', views.name_room_list, name='name_room_list'),
    path('room_cts_list/', views.room_cts_list, name='room_cts_list'),
    path('get_old_bill/', views.get_old_bill, name='get_old_bill'),
    path('report_page/', views.report_page, name='report_page'),
    path('load_cts_numbers/', views.load_cts_numbers, name='load_cts_numbers'),
    path('load_room_numbers/', views.load_room_numbers, name='load_room_numbers'),
    path('load_tenant_names/', views.load_tenant_names, name='load_tenant_names'),
]
