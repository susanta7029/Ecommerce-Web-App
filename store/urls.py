from django.urls import path
from . import views
from .views import add_product, product_detail, add_review, add_to_wishlist, wishlist, remove_from_wishlist, profile, order_detail

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
     path('logout/', views.user_logout, name='user_logout'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),  # 👈 add this
    path('update_quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('add-product/', add_product, name='add_product'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/add-review/', add_review, name='add_review'),
    path('product/<int:product_id>/add-to-wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/', profile, name='profile'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
]

