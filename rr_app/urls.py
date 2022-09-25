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
    path('get_old_bill/', views.get_old_bill, name='get_old_bill'),
    # path('tenant_bill/<bill_id>', views.tenant_bill, name='tenant_bill_update'),
]
