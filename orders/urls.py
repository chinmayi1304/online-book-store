from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('create/', views.order_create, name='order_create'),
    path("response/", views.handleresponse, name="handleresponse"),
    path("created/", views.thankpg, name="thankpg"),

]
