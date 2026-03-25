from django.urls import path
from .views import *

urlpatterns =[
    path('',index,name='index'),
    path('updatecart/',updatecart,name='updatecart'),
    path('register/',register,name='register'),
    path('logout/',mylogout,name="mylogout"),
    path('cart/',cart,name='cart'),
    path('checkout/',checkout,name='checkout'),
    path('config/', stripe_config,name='stripe_config'),
     path('create-checkout-session/', create_checkout_session,name='create_checkout_session'),
     path("success/",successview,name='successview'),
     path('cancelled',canview,name='canview'),
     path('webhook/', stripe_webhook),
     path('myorders/',myorders,name='myorders'),
     path('product_detail_view/<int:pid>/',product_detail_view,name='product_detail_view')
]