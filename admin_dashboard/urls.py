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
]
