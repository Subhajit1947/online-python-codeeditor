from django.urls import path
from . import views

urlpatterns = [
    path('', views.editor, name='editor'),
    path('execute/', views.execute_code, name='execute_code'),
]