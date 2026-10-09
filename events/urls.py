from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('setup-db/', views.setup_database, name='setup_database'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Registration
    path('register/', views.register_child, name='register_child'),
    path('register/success/<int:pk>/', views.registration_success, name='registration_success'),
    path('children/', views.child_list, name='child_list'),
    path('children/<int:pk>/', views.child_profile, name='child_profile'),
    path('children/<int:pk>/edit/', views.edit_child, name='edit_child'),
    path('children/<int:pk>/delete/', views.delete_child, name='delete_child'),
    path('children/<int:pk>/id-card/', views.id_card, name='id_card'),

    # Entry & Gift Verification
    path('entry/', views.entry_page, name='entry'),
    path('children/<int:pk>/record-entry/', views.record_entry, name='record_entry'),
    path('children/<int:pk>/record-gift/', views.record_gift, name='record_gift'),
    path('api/lookup/', views.api_lookup, name='api_lookup'),

    # Search
    path('search/', views.search, name='search'),

    # Reports
    path('reports/daily/', views.daily_report, name='daily_report'),

    # Event Settings
    path('settings/', views.event_settings, name='event_settings'),
    path('settings/change-day/', views.change_day, name='change_day'),

    # Export
    path('export/', views.export_data, name='export_data'),
]
