from django.urls import path

from core import views
from libs.utils import generate_random_code

urlpatterns = [
    # Home and basic pages
    path("", views.home, name="home-page"),
    path("about_us", views.about_us, name="about_us-page"),
    path("contact_us", views.contact_us, name="contact_us-page"),
    path("contact_us/contact-us-success", views.contact_us_success, name="contact-us-success"),
    path(f'contact_us/{generate_random_code()}', views.contact_redirect, name='redirect-to-contact-page'),
    path("error404", views.error404, name="error404-page"),
    
    # Shop and cart pages
    path("shop/", views.shop, name="shop-page"),
    path("cart", views.cart_view, name="cart-page"),
    path("checkout", views.process_checkout, name="process_checkout"),
    path("checkout/<int:id>", views.process_checkout, name="process_checkout"),
    
    # Cart actions
    path("adicionar_ao_carrinho/<int:cupcake_id>/", views.adicionar_ao_carrinho, name="adicionar_ao_carrinho"),
    path("remover_item_do_carrinho/<int:item_id>/", views.remover_item_do_carrinho, name="remover_item_do_carrinho"),
    path("atualizar_carrinho/", views.atualizar_carrinho, name="atualizar_carrinho"),
    path("atualizar_quantidade_carrinho/", views.atualizar_quantidade_carrinho, name="atualizar_quantidade_carrinho"),
    path("aplicar_cupom/", views.aplicar_cupom, name="aplicar_cupom"),

    # Product details and ratings
    path("product_details/<int:id>/", views.product_details, name="product_details-page"),
    path("add_to_cart/<int:id>/", views.product_details, name="add_to_cart"),
    path("register-rating/", views.register_rating, name="register_rating"),

    # Address management
    path("registe_address", views.registe_address, name="registe_address"),
    path("edit-address/<str:token>/<int:id>/", views.edit_address, name="edit_address"),
    path(f'delete-address/{generate_random_code(5)}/<int:id>/', views.delete_address, name="delete_address"),

    # Image serving
    path("image/<str:page>/<str:_type>/<str:name>/", views.get_image, name="get_image"),

    # User account
    path("accounts/register/", views.register_view, name="register-page",),
    path("accounts/my_account/",views.my_account,name="user_account-page",),
    path("accounts/logout/",views.logout_view,name="logout-page",),
    path("accounts/login/", views.login_view, name="login-page"),

    # subscribe newsletter
    path('newsletters/subscribe', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('newsletters/unsubscribe/<str:email>/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),

]