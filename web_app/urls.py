from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    #  DASHBOARD
    path('', views.dashboard_view, name='dashboard'),

    #  FARMS
    path('farms/', views.farm_list_view, name='farm_list'),
    path('farms/new/', views.farm_create_view, name='farm_create'),
    path('farms/<int:pk>/', views.farm_detail_view, name='farm_detail'),
    path('farms/<int:pk>/edit/', views.farm_edit_view, name='farm_edit'),
    path('farms/<int:pk>/delete/', views.farm_delete_view, name='farm_delete'),

    #  HARVEST SCHEDULES
    path('harvests/', views.harvest_list_view, name='harvest_list'),
    path('farms/<int:farm_pk>/harvests/new/', views.harvest_create_view, name='harvest_create'),
    path('harvests/<int:pk>/status/', views.harvest_update_status_view, name='harvest_update_status'),

    #  PRODUCTS
    path('products/', views.product_list_view, name='product_list'),
    path('products/new/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    #  ORDERS
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/place/<int:product_pk>/', views.order_create_view, name='order_create'),
    path('orders/<int:pk>/confirm/', views.order_confirm_view, name='order_confirm'),
    path('orders/<int:pk>/status/', views.order_update_status_view, name='order_update_status'),

    #  DISPUTES
    path('disputes/', views.dispute_list_view, name='dispute_list'),
    path('orders/<int:order_pk>/dispute/', views.dispute_create_view, name='dispute_create'),
    path('disputes/<int:pk>/resolve/', views.dispute_resolve_view, name='dispute_resolve'),

    #  LOGISTICS — VEHICLES
    path('vehicles/', views.vehicle_list_view, name='vehicle_list'),
    path('vehicles/new/', views.vehicle_create_view, name='vehicle_create'),

    #  LOGISTICS — ROUTES
    path('routes/', views.route_list_view, name='route_list'),

    #  LOGISTICS — SHIPMENTS
    path('shipments/', views.shipment_list_view, name='shipment_list'),
    path('shipments/<int:pk>/', views.shipment_detail_view, name='shipment_detail'),
    path('shipments/<int:pk>/status/', views.shipment_update_status_view, name='shipment_update_status'),

    #  COLD CHAIN — FACILITIES
    path('cold-storage/', views.cold_storage_list_view, name='cold_storage_list'),
    path('cold-storage/<int:pk>/', views.cold_storage_detail_view, name='cold_storage_detail'),

    #  COLD CHAIN — BOOKINGS
    path('cold-storage/<int:facility_pk>/book/', views.cold_storage_book_view, name='cold_storage_book'),
    path('cold-storage/bookings/<int:pk>/', views.cold_storage_booking_detail_view, name='cold_storage_booking_detail'),
    path('cold-storage/bookings/<int:booking_pk>/temperatures/', views.temperature_log_view, name='temperature_logs'),

    #  ANALYTICS
    path('analytics/', views.analytics_dashboard_view, name='analytics_dashboard'),
    path('analytics/market-prices/', views.market_prices_view, name='market_prices'),
    path('analytics/loss-reports/', views.loss_report_list_view, name='loss_report_list'),
    path('analytics/loss-reports/new/', views.loss_report_create_view, name='loss_report_create'),

    #  NOTIFICATIONS
    path('notifications/', views.notification_list_view, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_mark_read_view, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read_view, name='notification_mark_all_read'),

    #  JSON API — SHIPMENT GPS
    path('api/shipments/<int:pk>/location/', views.api_shipment_location_view, name='api_shipment_location'),

    #  JSON API — TEMPERATURE
    path('api/bookings/<int:booking_pk>/temperature/', views.api_temperature_latest_view, name='api_temperature_latest'),

    #  JSON API — PRODUCTS
    path('api/products/search/', views.api_product_search_view, name='api_product_search'),

    #  JSON API — MARKET PRICES
    path('api/market-prices/', views.api_market_prices_view, name='api_market_prices'),

    #  JSON API — VEHICLE GPS
    path('api/vehicles/<int:vehicle_pk>/location/', views.api_update_vehicle_location_view, name='api_update_vehicle_location'),
]
