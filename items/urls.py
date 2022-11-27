from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('item/<int:id>/', views.get_item, name='items'),
    path('buy/<int:id>/', views.buy_item, name='buy'),
    path('order/<int:id>/', views.get_order, name='get_order'),
    path('buy_order/<int:id>/', views.buy_order, name='buy_order'),
    path('success/', views.success, name='success'),
    path('bad_request/', views.bad_request, name='bad_request')
]
