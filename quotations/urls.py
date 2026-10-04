from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:customer_id>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:customer_id>/delete/", views.customer_delete, name="customer_delete"),

    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:product_id>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete"),

    path("quotation/create/", views.quotation_create, name="quotation_create"),
    path("quotation/<int:quotation_id>/", views.quotation_detail, name="quotation_detail"),
    path("quotation/<int:quotation_id>/pdf/", views.quotation_pdf, name="quotation_pdf"),
    path("quotation/<int:quotation_id>/whatsapp/", views.quotation_whatsapp, name="quotation_whatsapp"),
]
