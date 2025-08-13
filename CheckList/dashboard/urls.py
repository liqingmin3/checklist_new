from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('checklists/', views.checklist_list, name='checklist_list'),
    path('templates/', views.template_list, name='template_list'),
    path('template/<int:template_id>/', views.template_detail, name='template_detail'),
    path('template/<int:template_id>/publish/', views.publish_template, name='publish_template'),
    path('checklist/<int:checklist_id>/edit/', views.edit_checklist, name='edit_checklist'),
]
