# tasks/urls.py
from django.urls import path
from . import views # ייבוא ה-views מאותה תיקייה

urlpatterns = [
    # הכתובת הריקה ("/") תפעיל את הפונקציה index_view
    path('', views.index_view, name='index'), 
    path('add/', views.add_task_view, name='add_task'),
    # הכתובת "dashboard/" תפעיל את העמוד האישי
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
]