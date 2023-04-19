from django.urls import path
from . import views

urlpatterns=[
    path("event_information_re", views.eventinfo,name='eventinfo'),
    path("qrcodescanin", views.qrcodescanin, name="qrcodescan"),
    path("qrcodescanout", views.qrcodescanout, name="qrcodescanout"),
    path("categoryinfo", views.categoryinfo, name="categoryinfo"),
    path("registrations_kitna_hain_dekh_le", views.registrations_count),
    path("add_category", views.add_category),
    path("add_event", views.add_event),
    path("user_data", views.export_users),
    path("mainevent_data", views.export_mainevent),
    path("kitne_registration_hain_jaan_le", views.register_data),
    path("event_registrations", views.eventregistrations),
    path("make_payment", views.makepayment),
    path("event", views.export_event),
    path("event_users", views.export_event_users),
    path("qrcodeverify", views.qrcodeverify),
    path("maineventdata", views.maineventdata),
    path("number_of_scans", views.scans),
]