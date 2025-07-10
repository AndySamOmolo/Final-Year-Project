from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('manage-users', views.manage_users, name='manage_users'),
    path('add-users', views.add_user, name='add_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('add-bakery-item/', views.add_bakery_item, name='add_bakery_item'),
    path('report-dashboard/', views.report_dashboard, name='report_dashboard'),
    path('generate-report/<str:report_type>/', views.generate_pdf_report, name='generate_pdf_report'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit_topping/<int:topping_id>/', views.edit_topping, name='edit_topping'),
    path('delete_topping/<int:topping_id>/', views.delete_topping, name='delete_topping'),
    path('edit_size/<int:size_id>/', views.edit_size, name='edit_size'),
    path('delete_size/<int:size_id>/', views.delete_size, name='delete_size'),
    path('manage_bakery_items/', views.manage_bakery_items, name='manage_bakery_items'),
    path('edit_bakery_item/<int:item_id>/', views.edit_bakery_item, name='edit_bakery_item'),
    path('delete_bakery_item/<int:item_id>/', views.delete_bakery_item, name='delete_bakery_item'),
]
