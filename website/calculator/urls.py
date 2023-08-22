from django.urls import path
from . import views

urlpatterns = [
    path("", views.indexView), 
    path("result", views.resultView),
    path("result_m", views.result_m),
    path("result_f", views.result_f),
    path("special_form", views.special_form),
    path("special_score", views.special_score),
    path("search_stock", views.search_stock),
    path("result_stock", views.result_stock),
    path('search_house', views.search_house),
    path('result_house', views.result_house),
    path('dist_list', views.create_dist),
    path('load_town', views.load_town),
]