from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Notification,
    Farm, FarmerProfile, HarvestSchedule,
    ProductCategory, Product, PriceHistory,
    Vehicle, LogisticsRoute, Shipment, ShipmentTracking,
    Order, OrderItem, Dispute,
    ColdStorageFacility, ColdStorageBooking, TemperatureLog,
    PostHarvestLossReport, PlatformMetric, MarketPriceIndex,
)

admin.site.site_header = "🌾 AgriLogix Administration"
admin.site.site_title = "AgriLogix Admin"
admin.site.index_title = "Logistics in Agriculture Platform"


# ============================================================
# 👤 USERS
# ============================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'email', 'phone', 'role', 'is_verified', 'rating', 'total_transactions', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['-created_at']
    list_editable = ['is_verified']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = UserAdmin.fieldsets + (
        ('AgriLogix Profile', {
            'fields': ('role', 'phone', 'profile_photo', 'location', 'latitude', 'longitude',
                       'is_verified', 'rating', 'total_transactions', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('AgriLogix Profile', {
            'fields': ('role', 'phone', 'location')
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name() or '—'
    full_name.short_description = 'Full Name'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    list_editable = ['is_read']
    readonly_fields = ['created_at']


# ============================================================
# 🌾 FARMERS
# ============================================================

class HarvestScheduleInline(admin.TabularInline):
    model = HarvestSchedule
    extra = 1
    fields = ['product_name', 'expected_quantity_kg', 'harvest_date', 'ready_for_pickup_date', 'status']


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'farm_type', 'size_acres', 'location_name',
                    'nearest_town', 'has_storage', 'has_electricity', 'certification', 'is_active', 'created_at']
    list_filter = ['farm_type', 'has_storage', 'has_electricity', 'is_active', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__first_name', 'location_name', 'nearest_town']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    inlines = [HarvestScheduleInline]

    fieldsets = (
        ('Farm Identity', {'fields': ('owner', 'name', 'farm_type', 'description', 'size_acres', 'photo')}),
        ('Location', {'fields': ('location_name', 'latitude', 'longitude', 'nearest_town', 'distance_to_road_km')}),
        ('Infrastructure', {'fields': ('has_storage', 'has_electricity', 'water_source')}),
        ('Certification & Status', {'fields': ('certification', 'is_active', 'created_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cooperative_name', 'years_experience', 'preferred_payment',
                    'total_sales', 'savings_vs_middleman', 'is_premium', 'created_at']
    list_filter = ['preferred_payment', 'is_premium', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'cooperative_name', 'national_id']
    list_editable = ['is_premium']
    readonly_fields = ['total_sales', 'savings_vs_middleman', 'created_at']

    fieldsets = (
        ('Farmer Identity', {'fields': ('user', 'national_id', 'cooperative_name', 'years_experience', 'bio')}),
        ('Payment Details', {'fields': ('preferred_payment', 'mpesa_number', 'bank_account')}),
        ('Financial Performance', {'fields': ('total_sales', 'savings_vs_middleman', 'is_premium', 'created_at')}),
    )


@admin.register(HarvestSchedule)
class HarvestScheduleAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'farm', 'expected_quantity_kg', 'actual_quantity_kg',
                    'harvest_date', 'ready_for_pickup_date', 'status']
    list_filter = ['status', 'harvest_date']
    search_fields = ['product_name', 'farm__name']
    list_editable = ['status']
    date_hierarchy = 'harvest_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('farm__owner')


# ============================================================
# 🥦 PRODUCTS
# ============================================================

class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ['recorded_at']
    fields = ['price', 'market_price', 'notes', 'recorded_at']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'requires_cold_chain', 'min_temp_celsius', 'max_temp_celsius']
    list_filter = ['requires_cold_chain']
    search_fields = ['name']
    list_editable = ['requires_cold_chain']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm', 'category', 'quantity_available', 'unit',
                    'price_per_unit', 'total_value_display', 'is_organic', 'status', 'created_at']
    list_filter = ['status', 'category', 'is_organic', 'is_certified', 'created_at']
    search_fields = ['name', 'variety', 'farm__name', 'farm__owner__username']
    list_editable = ['status', 'price_per_unit']
    readonly_fields = ['views_count', 'created_at']
    inlines = [PriceHistoryInline]
    date_hierarchy = 'harvest_date'

    fieldsets = (
        ('Product Info', {'fields': ('farm', 'category', 'name', 'variety', 'description', 'photo')}),
        ('Inventory & Pricing', {'fields': ('quantity_available', 'unit', 'price_per_unit', 'minimum_order_quantity')}),
        ('Dates', {'fields': ('harvest_date', 'expiry_date')}),
        ('Quality & Status', {'fields': ('is_organic', 'is_certified', 'status', 'views_count', 'created_at')}),
    )

    def total_value_display(self, obj):
        return format_html('<b>KES {:,.0f}</b>', obj.total_value)
    total_value_display.short_description = 'Total Value'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('farm__owner', 'category')


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'market_price', 'price_diff', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['product__name']
    readonly_fields = ['recorded_at']

    def price_diff(self, obj):
        if obj.market_price:
            diff = obj.market_price - obj.price
            color = 'green' if diff > 0 else 'red'
            return format_html('<span style="color:{}">KES {:+,.0f}</span>', color, diff)
        return '—'
    price_diff.short_description = 'vs Market'


# ============================================================
# 🚛 LOGISTICS
# ============================================================

class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['latitude', 'longitude', 'speed_kmh', 'status_note', 'timestamp']
    max_num = 20


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'driver', 'vehicle_type', 'capacity_kg',
                    'is_refrigerated', 'status', 'insurance_expiry', 'inspection_expiry']
    list_filter = ['vehicle_type', 'is_refrigerated', 'status']
    search_fields = ['plate_number', 'make_model', 'driver__username']
    list_editable = ['status']
    readonly_fields = ['created_at', 'last_location_update']

    fieldsets = (
        ('Vehicle Info', {'fields': ('driver', 'vehicle_type', 'plate_number', 'make_model', 'year', 'capacity_kg', 'photo')}),
        ('Cold Chain Capability', {'fields': ('is_refrigerated', 'refrigeration_min_temp', 'refrigeration_max_temp')}),
        ('Compliance', {'fields': ('insurance_expiry', 'inspection_expiry')}),
        ('Live Status', {'fields': ('status', 'current_latitude', 'current_longitude', 'last_location_update', 'created_at')}),
    )


@admin.register(LogisticsRoute)
class LogisticsRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin_name', 'destination_name', 'distance_km',
                    'estimated_duration_hours', 'base_cost_per_kg',
                    'is_cold_chain_available', 'frequency', 'is_active']
    list_filter = ['is_cold_chain_available', 'is_active']
    search_fields = ['name', 'origin_name', 'destination_name']
    list_editable = ['is_active', 'base_cost_per_kg']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_code', 'driver', 'vehicle', 'status_badge', 'status',  # ← add 'status'
                    'weight_kg', 'shipping_cost', 'scheduled_pickup', 'actual_delivery', 'driver_rating']
    list_editable = ['status']

    list_filter = ['status', 'created_at', 'scheduled_pickup']
    search_fields = ['shipment_code', 'driver__username', 'pickup_address', 'delivery_address']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ShipmentTrackingInline]
    date_hierarchy = 'scheduled_pickup'

    fieldsets = (
        ('Shipment Identity', {'fields': ('shipment_code', 'driver', 'vehicle', 'route')}),
        ('Addresses', {'fields': ('pickup_address', 'pickup_latitude', 'pickup_longitude',
                                  'delivery_address', 'delivery_latitude', 'delivery_longitude')}),
        ('Timeline', {'fields': ('scheduled_pickup', 'actual_pickup', 'estimated_delivery', 'actual_delivery')}),
        ('Details', {'fields': ('status', 'weight_kg', 'shipping_cost', 'notes')}),
        ('Completion', {'fields': ('proof_of_delivery_photo', 'driver_rating', 'created_at', 'updated_at')}),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'assigned': '#4169E1',
            'picked_up': '#00CED1',
            'in_transit': '#1E90FF',
            'at_cold_storage': '#00BFFF',
            'out_for_delivery': '#FFD700',
            'delivered': '#32CD32',
            'failed': '#DC143C',
        }
        color = colors.get(obj.status, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('driver', 'vehicle', 'route')


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'latitude', 'longitude', 'speed_kmh', 'status_note', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['shipment__shipment_code', 'status_note']
    readonly_fields = ['timestamp']


# ============================================================
# 📦 ORDERS
# ============================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['product', 'quantity', 'unit_price', 'subtotal', 'requires_cold_chain', 'notes']


class DisputeInline(admin.StackedInline):
    model = Dispute
    extra = 0
    readonly_fields = ['created_at']
    fields = ['raised_by', 'reason', 'description', 'evidence_photo', 'status', 'resolution', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'farmer', 'status_badge', 'status',  # ← add 'status'
                    'subtotal', 'shipping_cost', 'total_amount', 'farmer_earnings_display',
                    'payment_method', 'created_at']

    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'buyer__username', 'farmer__username', 'payment_reference']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [OrderItemInline, DisputeInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Identity', {'fields': ('order_number', 'buyer', 'farmer', 'shipment', 'status')}),
        ('Financials', {'fields': ('subtotal', 'shipping_cost', 'platform_fee', 'total_amount',
                                   'payment_method', 'payment_reference', 'payment_date')}),
        ('Delivery', {'fields': ('delivery_address', 'delivery_latitude', 'delivery_longitude',
                                 'requested_delivery_date')}),
        ('Notes', {'fields': ('buyer_notes', 'farmer_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'completed_at')}),
    )

    def status_badge(self, obj):
        colors = {
            'draft': '#888888',
            'pending': '#FFA500',
            'confirmed': '#4169E1',
            'payment_pending': '#FF6347',
            'paid': '#32CD32',
            'processing': '#00CED1',
            'dispatched': '#1E90FF',
            'delivered': '#228B22',
            'completed': '#006400',
            'cancelled': '#DC143C',
            'disputed': '#FF4500',
        }
        color = colors.get(obj.status, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def farmer_earnings_display(self, obj):
        return format_html('<b style="color:green">KES {:,.2f}</b>', obj.farmer_earnings)
    farmer_earnings_display.short_description = 'Farmer Earnings'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('buyer', 'farmer')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'unit_price', 'subtotal', 'requires_cold_chain']
    list_filter = ['requires_cold_chain']
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = ['subtotal']


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['order', 'raised_by', 'reason', 'status', 'resolved_by', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['order__order_number', 'raised_by__username', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'resolved_at']


# ============================================================
# ❄️ COLD CHAIN
# ============================================================

class ColdStorageBookingInline(admin.TabularInline):
    model = ColdStorageBooking
    extra = 0
    readonly_fields = ['total_cost', 'created_at']
    fields = ['booked_by', 'product_description', 'quantity_tonnes',
              'start_date', 'end_date', 'total_cost', 'status']
    show_change_link = True


class TemperatureLogInline(admin.TabularInline):
    model = TemperatureLog
    extra = 0
    readonly_fields = ['recorded_at', 'alert_level']
    fields = ['sensor_id', 'temperature_celsius', 'humidity_percent', 'alert_level', 'recorded_at']
    max_num = 20


@admin.register(ColdStorageFacility)
class ColdStorageFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'location_name', 'capacity_display', 'utilization_bar',
                    'temp_range', 'cost_per_tonne_per_day', 'has_backup_generator', 'status']
    list_filter = ['status', 'has_backup_generator', 'is_active']
    search_fields = ['name', 'location_name', 'operator__username']
    list_editable = ['status']
    readonly_fields = ['created_at']
    inlines = [ColdStorageBookingInline]

    def capacity_display(self, obj):
        return f"{obj.available_capacity_tonnes:.1f} / {obj.total_capacity_tonnes:.1f} T"
    capacity_display.short_description = 'Available / Total'

    def utilization_bar(self, obj):
        pct = obj.utilization_percent
        color = '#32CD32' if pct < 70 else '#FFA500' if pct < 90 else '#DC143C'
        return format_html(
            '<div style="background:#eee;border-radius:4px;width:120px;height:16px">'
            '<div style="background:{};width:{}%;height:100%;border-radius:4px"></div>'
            '</div> {}%',
            color, pct, pct
        )
    utilization_bar.short_description = 'Utilization'

    def temp_range(self, obj):
        return f"{obj.min_temperature_celsius}°C to {obj.max_temperature_celsius}°C"
    temp_range.short_description = 'Temp Range'


@admin.register(ColdStorageBooking)
class ColdStorageBookingAdmin(admin.ModelAdmin):
    list_display = ['product_description', 'facility', 'booked_by', 'quantity_tonnes',
                    'start_date', 'end_date', 'duration_display', 'total_cost', 'status']
    list_filter = ['status', 'start_date', 'facility']
    search_fields = ['product_description', 'facility__name', 'booked_by__username']
    list_editable = ['status']
    readonly_fields = ['total_cost', 'created_at']
    inlines = [TemperatureLogInline]

    def duration_display(self, obj):
        return f"{obj.duration_days} days"
    duration_display.short_description = 'Duration'


@admin.register(TemperatureLog)
class TemperatureLogAdmin(admin.ModelAdmin):
    list_display = ['sensor_id', 'temperature_display', 'humidity_percent',
                    'alert_badge', 'booking', 'shipment', 'is_alert_sent', 'recorded_at']
    list_filter = ['alert_level', 'is_alert_sent', 'recorded_at']
    search_fields = ['sensor_id']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'

    def temperature_display(self, obj):
        color = {'critical': '#DC143C', 'warning': '#FFA500', 'normal': '#228B22'}.get(obj.alert_level, '#000')
        return format_html('<b style="color:{}">{:.1f}°C</b>', color, obj.temperature_celsius)
    temperature_display.short_description = 'Temperature'

    def alert_badge(self, obj):
        badges = {'normal': '🟢 Normal', 'warning': '🟡 Warning', 'critical': '🔴 CRITICAL'}
        return badges.get(obj.alert_level, obj.alert_level)
    alert_badge.short_description = 'Alert Level'


# ============================================================
# 📊 ANALYTICS
# ============================================================

@admin.register(PostHarvestLossReport)
class PostHarvestLossReportAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'farm', 'quantity_lost_kg', 'value_lost_display',
                    'primary_cause', 'was_cold_chain_used', 'incident_date']
    list_filter = ['primary_cause', 'was_cold_chain_used', 'incident_date']
    search_fields = ['product_name', 'farm__name', 'farm__owner__username']
    date_hierarchy = 'incident_date'
    readonly_fields = ['created_at']

    def value_lost_display(self, obj):
        return format_html('<span style="color:red">KES {:,.0f}</span>', obj.estimated_value_lost)
    value_lost_display.short_description = 'Value Lost'


@admin.register(PlatformMetric)
class PlatformMetricAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'completed_orders', 'gmv_display',
                    'farmer_earnings_display', 'middleman_savings_display',
                    'active_farmers', 'cold_chain_trips', 'spoilage_prevented_kg']
    list_filter = ['date']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'

    def gmv_display(self, obj):
        return format_html('<b>KES {:,.0f}</b>', obj.total_gmv)
    gmv_display.short_description = 'GMV'

    def farmer_earnings_display(self, obj):
        return format_html('<span style="color:green">KES {:,.0f}</span>', obj.total_farmer_earnings)
    farmer_earnings_display.short_description = 'Farmer Earnings'

    def middleman_savings_display(self, obj):
        return format_html('<span style="color:blue">KES {:,.0f}</span>', obj.total_middleman_savings)
    middleman_savings_display.short_description = 'Savings vs Middlemen'


@admin.register(MarketPriceIndex)
class MarketPriceIndexAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'market', 'price_per_kg', 'recorded_date']
    list_filter = ['market', 'recorded_date']
    search_fields = ['product_name']
    date_hierarchy = 'recorded_date'
    list_editable = ['price_per_kg']