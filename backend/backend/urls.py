from django.urls import path, re_path
from . import views

urlpatterns = [
    path("test/", views.testEnv, name="test"),
    path("", views.index, name="home"),
    re_path(r"api/upload_(?P<method>file|list)/", views.request_deck, name="input"),
    path("api/correct/", views.correct, name="correct"),
] 
