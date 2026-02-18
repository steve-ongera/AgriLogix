from django.contrib.auth.models import AbstractUser
from django.db import models


# ============================================================
# 👤 USERS
# ============================================================

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', '🌾 Farmer'),
        ('buyer', '🏪 Buyer / Market'),
        ('driver', '🚛 Logistics Driver'),
        ('cold_storage', '❄️ Cold Storage Operator'),
        ('admin', '⚙️ Platform Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_transactions = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Notification(models.Model):
    TYPES = [
        ('order', 'Order Update'),
        ('cold_chain', 'Cold Chain Alert'),
        ('delivery', 'Delivery Update'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} → {self.user.username}"

    class Meta:
        ordering = ['-created_at']


# ============================================================
# 🌾 FARMERS
# ============================================================

class Farm(models.Model):
    FARM_TYPES = [
        ('crop', 'Crop Farming'),
        ('vegetable', 'Vegetable Farming'),
        ('fruit', 'Fruit Farming'),
        ('mixed', 'Mixed Farming'),
        ('dairy', 'Dairy'),
        ('poultry', 'Poultry'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=255)
    farm_type = models.CharField(max_length=20, choices=FARM_TYPES)
    description = models.TextField(blank=True)
    size_acres = models.DecimalField(max_digits=10, decimal_places=2)
    location_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    nearest_town = models.CharField(max_length=100)
    distance_to_road_km = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    has_storage = models.BooleanField(default=False)
    has_electricity = models.BooleanField(default=False)
    water_source = models.CharField(max_length=100, blank=True)
    certification = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='farms/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.owner.get_full_name() or self.owner.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Farm"
        verbose_name_plural = "Farms"


class FarmerProfile(models.Model):
    PAYMENT_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    national_id = models.CharField(max_length=20, blank=True)
    cooperative_name = models.CharField(max_length=255, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    preferred_payment = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='mpesa')
    mpesa_number = models.CharField(max_length=15, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    savings_vs_middleman = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Farmer: {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"


class HarvestSchedule(models.Model):
    STATUS_CHOICES = [
        ('planned', '📅 Planned'),
        ('in_progress', '🌾 In Progress'),
        ('ready', '✅ Ready for Pickup'),
        ('collected', '🚛 Collected'),
        ('completed', '✔️ Completed'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='harvests')
    product_name = models.CharField(max_length=100)
    expected_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    actual_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    harvest_date = models.DateField()
    ready_for_pickup_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} from {self.farm.name} — {self.harvest_date}"

    class Meta:
        ordering = ['harvest_date']
        verbose_name = "Harvest Schedule"
        verbose_name_plural = "Harvest Schedules"


# ============================================================
# 🥦 PRODUCTS
# ============================================================

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='🌿')
    requires_cold_chain = models.BooleanField(default=False)
    min_temp_celsius = models.IntegerField(null=True, blank=True)
    max_temp_celsius = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.icon} {self.name}"

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']


class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('tonne', 'Tonne (t)'),
        ('crate', 'Crate'),
        ('bag', 'Bag (90kg)'),
        ('litre', 'Litre'),
        ('dozen', 'Dozen'),
        ('unit', 'Unit'),
    ]

    STATUS_CHOICES = [
        ('available', '✅ Available'),
        ('reserved', '🔒 Reserved'),
        ('sold', '✔️ Sold Out'),
        ('expired', '❌ Expired'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    variety = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    harvest_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_organic = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='products/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit}) — {self.farm.name}"

    @property
    def total_value(self):
        return self.quantity_available * self.price_per_unit

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    market_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text="Nairobi wholesale price for comparison")
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product.name}: KES {self.price} on {self.recorded_at.date()}"

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"


# ============================================================
# 🚛 LOGISTICS
# ============================================================

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('motorcycle', '🏍️ Motorcycle'),
        ('pickup', '🚐 Pickup Truck'),
        ('truck_small', '🚛 Small Truck (1-3T)'),
        ('truck_medium', '🚚 Medium Truck (3-7T)'),
        ('truck_large', '🏗️ Large Truck (7T+)'),
        ('refrigerated', '❄️ Refrigerated Truck'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    plate_number = models.CharField(max_length=20, unique=True)
    make_model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    capacity_kg = models.DecimalField(max_digits=8, decimal_places=2)
    is_refrigerated = models.BooleanField(default=False)
    refrigeration_min_temp = models.IntegerField(null=True, blank=True)
    refrigeration_max_temp = models.IntegerField(null=True, blank=True)
    insurance_expiry = models.DateField()
    inspection_expiry = models.DateField()
    photo = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} — {self.get_vehicle_type_display()} ({self.driver.get_full_name()})"

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"


class LogisticsRoute(models.Model):
    name = models.CharField(max_length=200)
    origin_name = models.CharField(max_length=200)
    origin_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    origin_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_name = models.CharField(max_length=200)
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    base_cost_per_kg = models.DecimalField(max_digits=8, decimal_places=4)
    is_cold_chain_available = models.BooleanField(default=False)
    frequency = models.CharField(max_length=50, default='Daily')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin_name} → {self.destination_name}"

    class Meta:
        verbose_name = "Logistics Route"
        verbose_name_plural = "Logistics Routes"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ Pending Assignment'),
        ('assigned', '📋 Driver Assigned'),
        ('picked_up', '🚛 Picked Up'),
        ('in_transit', '🛣️ In Transit'),
        ('at_cold_storage', '❄️ At Cold Storage'),
        ('out_for_delivery', '📦 Out for Delivery'),
        ('delivered', '✅ Delivered'),
        ('failed', '❌ Failed'),
    ]

    shipment_code = models.CharField(max_length=20, unique=True)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='shipments', limit_choices_to={'role': 'driver'})
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='shipments')
    route = models.ForeignKey(LogisticsRoute, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='shipments')
    pickup_address = models.CharField(max_length=300)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_address = models.CharField(max_length=300)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_pickup = models.DateTimeField()
    actual_pickup = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    proof_of_delivery_photo = models.ImageField(upload_to='deliveries/', null=True, blank=True)
    driver_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment #{self.shipment_code}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"


class ShipmentTracking(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_events')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status_note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipment.shipment_code} @ {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Tracking Event"
        verbose_name_plural = "Tracking Events"


# ============================================================
# 📦 ORDERS
# ============================================================

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', '📝 Draft'),
        ('pending', '⏳ Pending Farmer Confirmation'),
        ('confirmed', '✅ Confirmed'),
        ('payment_pending', '💳 Payment Pending'),
        ('paid', '💰 Paid'),
        ('processing', '⚙️ Processing'),
        ('dispatched', '🚛 Dispatched'),
        ('delivered', '📦 Delivered'),
        ('completed', '🎉 Completed'),
        ('cancelled', '❌ Cancelled'),
        ('disputed', '⚠️ Disputed'),
    ]

    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
        ('escrow', 'AgriLogix Escrow'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_placed',
                               limit_choices_to={'role': 'buyer'})
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_received',
                                limit_choices_to={'role': 'farmer'})
    shipment = models.OneToOneField(Shipment, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='order')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    delivery_address = models.CharField(max_length=300)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    requested_delivery_date = models.DateField(null=True, blank=True)
    buyer_notes = models.TextField(blank=True)
    farmer_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.order_number} ({self.buyer.username} → {self.farmer.username})"

    @property
    def farmer_earnings(self):
        return self.subtotal - self.platform_fee

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    requires_cold_chain = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} {self.product.unit} of {self.product.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class Dispute(models.Model):
    REASONS = [
        ('quality', 'Poor Product Quality'),
        ('quantity', 'Wrong Quantity'),
        ('not_delivered', 'Not Delivered'),
        ('late_delivery', 'Late Delivery'),
        ('payment', 'Payment Issue'),
        ('other', 'Other'),
    ]

    STATUS = [
        ('open', '🔴 Open'),
        ('investigating', '🟡 Under Investigation'),
        ('resolved', '🟢 Resolved'),
        ('escalated', '🟠 Escalated'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes_raised')
    reason = models.CharField(max_length=20, choices=REASONS)
    description = models.TextField()
    evidence_photo = models.ImageField(upload_to='disputes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='disputes_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispute on Order #{self.order.order_number} — {self.get_reason_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Dispute"
        verbose_name_plural = "Disputes"


# ============================================================
# ❄️ COLD CHAIN
# ============================================================

class ColdStorageFacility(models.Model):
    STATUS_CHOICES = [
        ('operational', '✅ Operational'),
        ('full', '🔴 Full Capacity'),
        ('maintenance', '🔧 Under Maintenance'),
        ('offline', '⚫ Offline'),
    ]

    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facilities',
                                  limit_choices_to={'role': 'cold_storage'})
    name = models.CharField(max_length=200)
    location_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    total_capacity_tonnes = models.DecimalField(max_digits=10, decimal_places=2)
    available_capacity_tonnes = models.DecimalField(max_digits=10, decimal_places=2)
    min_temperature_celsius = models.IntegerField(default=2)
    max_temperature_celsius = models.IntegerField(default=8)
    cost_per_tonne_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    has_backup_generator = models.BooleanField(default=False)
    certification = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    photo = models.ImageField(upload_to='cold_storage/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.location_name})"

    @property
    def utilization_percent(self):
        if self.total_capacity_tonnes == 0:
            return 0
        used = self.total_capacity_tonnes - self.available_capacity_tonnes
        return round((used / self.total_capacity_tonnes) * 100, 1)

    class Meta:
        verbose_name = "Cold Storage Facility"
        verbose_name_plural = "Cold Storage Facilities"


class ColdStorageBooking(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    facility = models.ForeignKey(ColdStorageFacility, on_delete=models.CASCADE, related_name='bookings')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='cold_storage_bookings')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cold_storage_bookings')
    product_description = models.CharField(max_length=200)
    quantity_tonnes = models.DecimalField(max_digits=8, decimal_places=3)
    required_temp_min = models.IntegerField()
    required_temp_max = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days

    def save(self, *args, **kwargs):
        self.total_cost = (
            self.quantity_tonnes *
            self.facility.cost_per_tonne_per_day *
            max(self.duration_days, 1)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_description} @ {self.facility.name} ({self.start_date} – {self.end_date})"

    class Meta:
        verbose_name = "Cold Storage Booking"
        verbose_name_plural = "Cold Storage Bookings"


class TemperatureLog(models.Model):
    ALERT_LEVELS = [
        ('normal', '🟢 Normal'),
        ('warning', '🟡 Warning'),
        ('critical', '🔴 Critical — Spoilage Risk'),
    ]

    booking = models.ForeignKey(ColdStorageBooking, on_delete=models.CASCADE,
                                 related_name='temperature_logs', null=True, blank=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE,
                                  related_name='temperature_logs', null=True, blank=True)
    sensor_id = models.CharField(max_length=50)
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2)
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS, default='normal')
    is_alert_sent = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sensor {self.sensor_id}: {self.temperature_celsius}°C [{self.get_alert_level_display()}]"

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "Temperature Log"
        verbose_name_plural = "Temperature Logs"


# ============================================================
# 📊 ANALYTICS
# ============================================================

class PostHarvestLossReport(models.Model):
    CAUSE_CHOICES = [
        ('temperature', 'Temperature Abuse'),
        ('transport_delay', 'Transport Delay'),
        ('handling', 'Poor Handling'),
        ('packaging', 'Packaging Failure'),
        ('road_condition', 'Bad Road Conditions'),
        ('breakdown', 'Vehicle Breakdown'),
        ('other', 'Other'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='loss_reports')
    product_name = models.CharField(max_length=100)
    quantity_lost_kg = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_value_lost = models.DecimalField(max_digits=12, decimal_places=2)
    primary_cause = models.CharField(max_length=20, choices=CAUSE_CHOICES)
    description = models.TextField(blank=True)
    was_cold_chain_used = models.BooleanField(default=False)
    incident_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loss: {self.quantity_lost_kg}kg {self.product_name} from {self.farm.name}"

    class Meta:
        ordering = ['-incident_date']
        verbose_name = "Post-Harvest Loss Report"
        verbose_name_plural = "Post-Harvest Loss Reports"


class PlatformMetric(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    total_gmv = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_farmer_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_middleman_savings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    active_farmers = models.PositiveIntegerField(default=0)
    active_buyers = models.PositiveIntegerField(default=0)
    active_drivers = models.PositiveIntegerField(default=0)
    shipments_completed = models.PositiveIntegerField(default=0)
    kg_transported = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cold_chain_trips = models.PositiveIntegerField(default=0)
    spoilage_prevented_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    temperature_alerts_sent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Metrics for {self.date}: GMV KES {self.total_gmv:,.0f}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Platform Metric"
        verbose_name_plural = "Platform Metrics"


class MarketPriceIndex(models.Model):
    MARKETS = [
        ('nairobi_wakulima', 'Wakulima Market, Nairobi'),
        ('nairobi_kangemi', 'Kangemi Market, Nairobi'),
        ('mombasa_kongowea', 'Kongowea Market, Mombasa'),
        ('kisumu_kibuye', 'Kibuye Market, Kisumu'),
        ('nakuru_central', 'Central Market, Nakuru'),
    ]

    market = models.CharField(max_length=30, choices=MARKETS)
    product_name = models.CharField(max_length=100)
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    recorded_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} @ {self.get_market_display()}: KES {self.price_per_kg}/kg"

    class Meta:
        ordering = ['-recorded_date']
        verbose_name = "Market Price Index"
        verbose_name_plural = "Market Price Indices"