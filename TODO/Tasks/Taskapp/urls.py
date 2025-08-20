from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),  
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('add/', views.add_task, name='add_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('daily-plan/', views.daily_plan_view, name='daily_plan'),
    # path('daily-plan/update/<int:plan_id>/',views. update_plan, name='update_plan'),
    path('daily-plan/delete/<int:plan_id>/', views.delete_plan, name='delete_plan'),
    # path("daily-plan/", views.daily_plan, name="daily_plan"),
    path('daily-plan/delete/<int:pk>/', views.delete_plan, name='delete_plan'),
    path("daily-plan/download/", views.download_excel, name="download_excel"),
    path("download_all_users_excel/", views.download_all_users_excel, name="download_all_users_excel"),
    path('admin_index', views.admin, name='admin_index'),
    path('admin_register/', views.AdminLogins, name='admin_register'),
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('admin_logout/', views.admin_logout_view, name='admin_logout'),
    path('delete-employee/<int:user_id>/', views.delete_employee, name='delete_employee'),
    path('change-password/', views.change_password_view, name='change_password'),


]