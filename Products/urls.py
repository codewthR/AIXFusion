
from django.urls import path
from . import views

urlpatterns = [
    path('products',views.presenting, name='products'),
    # path('uploads', views.upload_and_convert, name='uploads'),
    path('upload', views.home, name='upload'),
    path('convert/', views.convert_to_ppt, name='convert'),

    path('uplo', views.generate_ppt, name='uplo'),
    # path('converting', views.convert_text_to_ppt, name='converting'),
]