from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("document-types/", views.doc_type_list, name="doc_type_list"),
    path("document-types/new/", views.doc_type_create, name="doc_type_create"),
    path("document-types/<int:pk>/edit/", views.doc_type_update, name="doc_type_update"),
    path("document-types/<int:pk>/delete/", views.doc_type_delete, name="doc_type_delete"),

    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/edit/", views.request_update, name="request_update"),
    path("requests/<int:pk>/delete/", views.request_delete, name="request_delete"),
    path("requests/<int:pk>/process/", views.request_process, name="request_process"),

    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/new/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/delete/", views.appointment_delete, name="appointment_delete"),
    path("appointments/<int:pk>/process/", views.appointment_process, name="appointment_process"),

    path("payments/", views.payment_list, name="payment_list"),
    path("payments/new/", views.payment_create, name="payment_create"),
    path("payments/<int:pk>/edit/", views.payment_update, name="payment_update"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),
    path("payments/<int:pk>/process/", views.payment_process, name="payment_process"),

    path("inquiries/", views.inquiry_list, name="inquiry_list"),
    path("inquiries/new/", views.inquiry_create, name="inquiry_create"),
    path("inquiries/<int:pk>/edit/", views.inquiry_update, name="inquiry_update"),
    path("inquiries/<int:pk>/delete/", views.inquiry_delete, name="inquiry_delete"),
    path("inquiries/<int:pk>/process/", views.inquiry_process, name="inquiry_process"),
]
