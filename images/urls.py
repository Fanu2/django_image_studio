from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('', views.gallery, name='gallery'),  # main page
    path('upload/', views.upload_image, name='upload_image'),
    path('manipulate/<int:pk>/', views.manipulate_image, name='manipulate_image'),
    path('delete/<int:pk>/', views.delete_image, name='delete_image'),
]
