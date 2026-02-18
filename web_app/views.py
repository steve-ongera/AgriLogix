from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import json

from .models import (
    User, Notification,
    Farm, FarmerProfile, HarvestSchedule,
    ProductCategory, Product, PriceHistory,
    Vehicle, LogisticsRoute, Shipment, ShipmentTracking,
    Order, OrderItem, Dispute,
    ColdStorageFacility, ColdStorageBooking, TemperatureLog,
    PostHarvestLossReport, PlatformMetric, MarketPriceIndex,
)


# ============================================================
# 🔐 AUTH
# ============================================================

def register_view(request):
    if request.method == 'POST':
        username    = request.POST['username']
        email       = request.POST['email']
        password    = request.POST['password']
        first_name  = request.POST['first_name']
        last_name   = request.POST['last_name']
        role        = request.POST['role']
        phone       = request.POST.get('phone', '')
        location    = request.POST.get('location', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/register.html')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name,
            role=role, phone=phone, location=location,
        )
        login(request, user)
        messages.success(request, f'Welcome to AgriLogix, {user.first_name}!')
        return redirect('dashboard')

    return render(request, 'auth/register.html', {
        'roles': User.ROLE_CHOICES,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    farmer_profile = getattr(user, 'farmer_profile', None)
    farms = user.farms.all() if user.role == 'farmer' else None

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name  = request.POST.get('last_name', user.last_name)
        user.email      = request.POST.get('email', user.email)
        user.phone      = request.POST.get('phone', user.phone)
        user.location   = request.POST.get('location', user.location)
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'auth/profile.html', {
        'user': user,
        'farmer_profile': farmer_profile,
        'farms': farms,
    })


# ============================================================
# 🏠 DASHBOARD
# ============================================================

@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    if user.role == 'farmer':
        farms = Farm.objects.filter(owner=user)
        context.update({
            'farms': farms,
            'total_products': Product.objects.filter(farm__owner=user, status='available').count(),
            'pending_orders': Order.objects.filter(farmer=user, status='pending').count(),
            'total_earnings': Order.objects.filter(farmer=user, status='completed').aggregate(
                total=Sum('subtotal'))['total'] or 0,
            'recent_orders': Order.objects.filter(farmer=user).order_by('-created_at')[:5],
            'harvest_schedules': HarvestSchedule.objects.filter(
                farm__owner=user, status__in=['planned', 'ready']).order_by('harvest_date')[:5],
            'loss_reports': PostHarvestLossReport.objects.filter(
                farm__owner=user).order_by('-incident_date')[:3],
        })

    elif user.role == 'buyer':
        context.update({
            'recent_orders': Order.objects.filter(buyer=user).order_by('-created_at')[:5],
            'active_orders': Order.objects.filter(
                buyer=user, status__in=['confirmed', 'processing', 'dispatched']).count(),
            'completed_orders': Order.objects.filter(buyer=user, status='completed').count(),
            'total_spent': Order.objects.filter(buyer=user, status='completed').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'featured_products': Product.objects.filter(status='available').order_by('-created_at')[:6],
        })

    elif user.role == 'driver':
        context.update({
            'active_shipments': Shipment.objects.filter(
                driver=user, status__in=['assigned', 'picked_up', 'in_transit']),
            'completed_shipments': Shipment.objects.filter(driver=user, status='delivered').count(),
            'total_earnings': Shipment.objects.filter(driver=user, status='delivered').aggregate(
                total=Sum('shipping_cost'))['total'] or 0,
            'available_routes': LogisticsRoute.objects.filter(is_active=True)[:5],
            'my_vehicles': Vehicle.objects.filter(driver=user),
        })

    elif user.role == 'cold_storage':
        facilities = ColdStorageFacility.objects.filter(operator=user)
        context.update({
            'facilities': facilities,
            'active_bookings': ColdStorageBooking.objects.filter(
                facility__operator=user, status='active').count(),
            'temperature_alerts': TemperatureLog.objects.filter(
                booking__facility__operator=user,
                alert_level__in=['warning', 'critical']).order_by('-recorded_at')[:10],
        })

    elif user.role == 'admin':
        today = date.today()
        context.update({
            'total_farmers': User.objects.filter(role='farmer').count(),
            'total_buyers': User.objects.filter(role='buyer').count(),
            'total_orders': Order.objects.count(),
            'total_gmv': Order.objects.filter(status='completed').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'pending_disputes': Dispute.objects.filter(status='open').count(),
            'recent_metrics': PlatformMetric.objects.order_by('-date')[:7],
            'critical_alerts': TemperatureLog.objects.filter(
                alert_level='critical').order_by('-recorded_at')[:5],
        })

    context['notifications'] = Notification.objects.filter(
        user=user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'dashboard.html', context)


# ============================================================
# 🌾 FARMS
# ============================================================

@login_required
def farm_list_view(request):
    farms = Farm.objects.filter(is_active=True).select_related('owner')
    farm_type = request.GET.get('type')
    county    = request.GET.get('county')
    if farm_type:
        farms = farms.filter(farm_type=farm_type)
    if county:
        farms = farms.filter(location_name__icontains=county)
    return render(request, 'farms/list.html', {
        'farms': farms,
        'farm_types': Farm.FARM_TYPES,
    })


@login_required
def farm_detail_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk)
    products = Product.objects.filter(farm=farm, status='available')
    harvests = HarvestSchedule.objects.filter(farm=farm).order_by('harvest_date')
    loss_reports = PostHarvestLossReport.objects.filter(farm=farm).order_by('-incident_date')
    return render(request, 'farms/detail.html', {
        'farm': farm,
        'products': products,
        'harvests': harvests,
        'loss_reports': loss_reports,
    })


@login_required
def farm_create_view(request):
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can register farms.')
        return redirect('dashboard')

    if request.method == 'POST':
        farm = Farm.objects.create(
            owner=request.user,
            name=request.POST['name'],
            farm_type=request.POST['farm_type'],
            description=request.POST.get('description', ''),
            size_acres=request.POST['size_acres'],
            location_name=request.POST['location_name'],
            latitude=request.POST['latitude'],
            longitude=request.POST['longitude'],
            nearest_town=request.POST['nearest_town'],
            distance_to_road_km=request.POST.get('distance_to_road_km', 0),
            has_storage=request.POST.get('has_storage') == 'on',
            has_electricity=request.POST.get('has_electricity') == 'on',
            water_source=request.POST.get('water_source', ''),
            certification=request.POST.get('certification', ''),
            photo=request.FILES.get('photo'),
        )
        messages.success(request, f'Farm "{farm.name}" registered successfully!')
        return redirect('farm_detail', pk=farm.pk)

    return render(request, 'farms/create.html', {
        'farm_types': Farm.FARM_TYPES,
    })


@login_required
def farm_edit_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        farm.name             = request.POST.get('name', farm.name)
        farm.description      = request.POST.get('description', farm.description)
        farm.size_acres       = request.POST.get('size_acres', farm.size_acres)
        farm.location_name    = request.POST.get('location_name', farm.location_name)
        farm.nearest_town     = request.POST.get('nearest_town', farm.nearest_town)
        farm.has_storage      = request.POST.get('has_storage') == 'on'
        farm.has_electricity  = request.POST.get('has_electricity') == 'on'
        farm.water_source     = request.POST.get('water_source', farm.water_source)
        farm.certification    = request.POST.get('certification', farm.certification)
        if 'photo' in request.FILES:
            farm.photo = request.FILES['photo']
        farm.save()
        messages.success(request, 'Farm updated successfully.')
        return redirect('farm_detail', pk=farm.pk)

    return render(request, 'farms/edit.html', {'farm': farm, 'farm_types': Farm.FARM_TYPES})


@login_required
def farm_delete_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        farm.is_active = False
        farm.save()
        messages.success(request, f'Farm "{farm.name}" deactivated.')
        return redirect('dashboard')
    return render(request, 'farms/confirm_delete.html', {'farm': farm})


# ============================================================
# 📅 HARVEST SCHEDULES
# ============================================================

@login_required
def harvest_list_view(request):
    harvests = HarvestSchedule.objects.filter(
        farm__owner=request.user
    ).select_related('farm').order_by('harvest_date')
    return render(request, 'harvests/list.html', {'harvests': harvests})


@login_required
def harvest_create_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    if request.method == 'POST':
        HarvestSchedule.objects.create(
            farm=farm,
            product_name=request.POST['product_name'],
            expected_quantity_kg=request.POST['expected_quantity_kg'],
            harvest_date=request.POST['harvest_date'],
            ready_for_pickup_date=request.POST['ready_for_pickup_date'],
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Harvest schedule added.')
        return redirect('farm_detail', pk=farm.pk)
    return render(request, 'harvests/create.html', {'farm': farm})


@login_required
def harvest_update_status_view(request, pk):
    harvest = get_object_or_404(HarvestSchedule, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        harvest.status = request.POST['status']
        harvest.actual_quantity_kg = request.POST.get('actual_quantity_kg') or None
        harvest.save()
        messages.success(request, 'Harvest status updated.')
    return redirect('farm_detail', pk=harvest.farm.pk)


# ============================================================
# 🥦 PRODUCTS
# ============================================================

@login_required
def product_list_view(request):
    products = Product.objects.filter(status='available').select_related('farm__owner', 'category')
    category_id = request.GET.get('category')
    is_organic  = request.GET.get('organic')
    min_price   = request.GET.get('min_price')
    max_price   = request.GET.get('max_price')
    search      = request.GET.get('q')

    if category_id:
        products = products.filter(category_id=category_id)
    if is_organic:
        products = products.filter(is_organic=True)
    if min_price:
        products = products.filter(price_per_unit__gte=min_price)
    if max_price:
        products = products.filter(price_per_unit__lte=max_price)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(variety__icontains=search) |
            Q(farm__name__icontains=search) |
            Q(farm__location_name__icontains=search)
        )

    categories = ProductCategory.objects.all()
    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories,
    })


@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.views_count += 1
    product.save(update_fields=['views_count'])

    price_history = PriceHistory.objects.filter(product=product).order_by('-recorded_at')[:10]
    market_prices = MarketPriceIndex.objects.filter(
        product_name__icontains=product.name.split('(')[0].strip()
    ).order_by('-recorded_date')[:5]

    return render(request, 'products/detail.html', {
        'product': product,
        'price_history': price_history,
        'market_prices': market_prices,
    })


@login_required
def product_create_view(request):
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can list products.')
        return redirect('product_list')

    farms = Farm.objects.filter(owner=request.user, is_active=True)
    categories = ProductCategory.objects.all()

    if request.method == 'POST':
        product = Product.objects.create(
            farm=get_object_or_404(Farm, pk=request.POST['farm'], owner=request.user),
            category=get_object_or_404(ProductCategory, pk=request.POST['category']),
            name=request.POST['name'],
            variety=request.POST.get('variety', ''),
            description=request.POST.get('description', ''),
            quantity_available=request.POST['quantity_available'],
            unit=request.POST['unit'],
            price_per_unit=request.POST['price_per_unit'],
            minimum_order_quantity=request.POST.get('minimum_order_quantity', 1),
            harvest_date=request.POST['harvest_date'],
            expiry_date=request.POST.get('expiry_date') or None,
            is_organic=request.POST.get('is_organic') == 'on',
            is_certified=request.POST.get('is_certified') == 'on',
            photo=request.FILES.get('photo'),
        )
        messages.success(request, f'"{product.name}" listed successfully!')
        return redirect('product_detail', pk=product.pk)

    return render(request, 'products/create.html', {
        'farms': farms,
        'categories': categories,
        'unit_choices': Product.UNIT_CHOICES,
    })


@login_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farm__owner=request.user)
    categories = ProductCategory.objects.all()

    if request.method == 'POST':
        product.name               = request.POST.get('name', product.name)
        product.variety            = request.POST.get('variety', product.variety)
        product.description        = request.POST.get('description', product.description)
        product.quantity_available = request.POST.get('quantity_available', product.quantity_available)
        product.price_per_unit     = request.POST.get('price_per_unit', product.price_per_unit)
        product.status             = request.POST.get('status', product.status)
        product.is_organic         = request.POST.get('is_organic') == 'on'
        product.expiry_date        = request.POST.get('expiry_date') or None
        if 'photo' in request.FILES:
            product.photo = request.FILES['photo']
        product.save()
        messages.success(request, 'Product updated.')
        return redirect('product_detail', pk=product.pk)

    return render(request, 'products/edit.html', {
        'product': product,
        'categories': categories,
        'unit_choices': Product.UNIT_CHOICES,
        'status_choices': Product.STATUS_CHOICES,
    })


@login_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        product.status = 'expired'
        product.save()
        messages.success(request, 'Product removed from listings.')
        return redirect('dashboard')
    return render(request, 'products/confirm_delete.html', {'product': product})


# ============================================================
# 📦 ORDERS
# ============================================================

@login_required
def order_list_view(request):
    user = request.user
    if user.role == 'buyer':
        orders = Order.objects.filter(buyer=user)
    elif user.role == 'farmer':
        orders = Order.objects.filter(farmer=user)
    else:
        orders = Order.objects.all()

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.select_related('buyer', 'farmer').order_by('-created_at')
    return render(request, 'orders/list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user not in [order.buyer, order.farmer] and request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('order_list')

    items    = OrderItem.objects.filter(order=order).select_related('product')
    disputes = Dispute.objects.filter(order=order)
    shipment = getattr(order, 'shipment', None)
    tracking = ShipmentTracking.objects.filter(
        shipment=shipment).order_by('-timestamp') if shipment else []

    return render(request, 'orders/detail.html', {
        'order': order,
        'items': items,
        'disputes': disputes,
        'shipment': shipment,
        'tracking': tracking,
    })


@login_required
def order_create_view(request, product_pk):
    if request.user.role != 'buyer':
        messages.error(request, 'Only buyers can place orders.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=product_pk, status='available')

    if request.method == 'POST':
        quantity   = float(request.POST['quantity'])
        unit_price = float(product.price_per_unit)
        subtotal   = quantity * unit_price
        fee        = subtotal * 0.025
        shipping   = float(request.POST.get('shipping_cost', 0))
        total      = subtotal + fee + shipping

        import uuid
        order_number = f"AGL-{date.today().year}-{str(uuid.uuid4())[:8].upper()}"

        order = Order.objects.create(
            order_number=order_number,
            buyer=request.user,
            farmer=product.farm.owner,
            subtotal=subtotal,
            platform_fee=fee,
            shipping_cost=shipping,
            total_amount=total,
            payment_method=request.POST['payment_method'],
            delivery_address=request.POST['delivery_address'],
            requested_delivery_date=request.POST.get('requested_delivery_date') or None,
            buyer_notes=request.POST.get('buyer_notes', ''),
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            requires_cold_chain=product.category.requires_cold_chain if product.category else False,
        )

        # Notify farmer
        Notification.objects.create(
            user=product.farm.owner,
            notification_type='order',
            title='New Order Received!',
            message=f'{request.user.get_full_name()} ordered {quantity}{product.unit} of {product.name}.',
        )

        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('order_detail', pk=order.pk)

    cold_chain_routes = LogisticsRoute.objects.filter(
        is_cold_chain_available=True, is_active=True
    ) if product.category and product.category.requires_cold_chain else []

    return render(request, 'orders/create.html', {
        'product': product,
        'payment_methods': Order.PAYMENT_METHODS,
        'cold_chain_routes': cold_chain_routes,
    })


@login_required
def order_confirm_view(request, pk):
    order = get_object_or_404(Order, pk=pk, farmer=request.user, status='pending')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            order.status = 'confirmed'
            order.farmer_notes = request.POST.get('farmer_notes', '')
            order.save()
            Notification.objects.create(
                user=order.buyer,
                notification_type='order',
                title='Order Confirmed!',
                message=f'Your order #{order.order_number} has been confirmed by the farmer.',
            )
            messages.success(request, 'Order confirmed.')
        elif action == 'cancel':
            order.status = 'cancelled'
            order.save()
            messages.warning(request, 'Order cancelled.')
    return redirect('order_detail', pk=order.pk)


@login_required
def order_update_status_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    allowed_roles = ['admin', 'farmer']
    if request.user.role not in allowed_roles and request.user != order.buyer:
        messages.error(request, 'Permission denied.')
        return redirect('order_detail', pk=pk)

    if request.method == 'POST':
        order.status = request.POST['status']
        if order.status == 'completed':
            order.completed_at = timezone.now()
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}.')
    return redirect('order_detail', pk=pk)


# ============================================================
# ⚠️ DISPUTES
# ============================================================

@login_required
def dispute_create_view(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.user not in [order.buyer, order.farmer]:
        messages.error(request, 'Access denied.')
        return redirect('order_detail', pk=order_pk)

    if request.method == 'POST':
        Dispute.objects.create(
            order=order,
            raised_by=request.user,
            reason=request.POST['reason'],
            description=request.POST['description'],
            evidence_photo=request.FILES.get('evidence_photo'),
        )
        order.status = 'disputed'
        order.save()
        messages.warning(request, 'Dispute raised. Our team will review within 24 hours.')
        return redirect('order_detail', pk=order_pk)

    return render(request, 'disputes/create.html', {
        'order': order,
        'reasons': Dispute.REASONS,
    })


@login_required
def dispute_list_view(request):
    if request.user.role == 'admin':
        disputes = Dispute.objects.all()
    else:
        disputes = Dispute.objects.filter(
            Q(raised_by=request.user) |
            Q(order__buyer=request.user) |
            Q(order__farmer=request.user)
        )
    status_filter = request.GET.get('status')
    if status_filter:
        disputes = disputes.filter(status=status_filter)
    return render(request, 'disputes/list.html', {
        'disputes': disputes.select_related('order', 'raised_by').order_by('-created_at'),
        'status_choices': Dispute.STATUS,
    })


@login_required
def dispute_resolve_view(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can resolve disputes.')
        return redirect('dispute_list')

    dispute = get_object_or_404(Dispute, pk=pk)
    if request.method == 'POST':
        dispute.status      = request.POST['status']
        dispute.resolution  = request.POST['resolution']
        dispute.resolved_by = request.user
        dispute.resolved_at = timezone.now()
        dispute.save()
        messages.success(request, 'Dispute resolved.')
    return redirect('dispute_list')


# ============================================================
# 🚛 LOGISTICS
# ============================================================

@login_required
def vehicle_list_view(request):
    if request.user.role == 'driver':
        vehicles = Vehicle.objects.filter(driver=request.user)
    else:
        vehicles = Vehicle.objects.filter(status='available').select_related('driver')
    return render(request, 'logistics/vehicle_list.html', {'vehicles': vehicles})


@login_required
def vehicle_create_view(request):
    if request.user.role != 'driver':
        messages.error(request, 'Only drivers can register vehicles.')
        return redirect('dashboard')

    if request.method == 'POST':
        Vehicle.objects.create(
            driver=request.user,
            vehicle_type=request.POST['vehicle_type'],
            plate_number=request.POST['plate_number'],
            make_model=request.POST['make_model'],
            year=request.POST['year'],
            capacity_kg=request.POST['capacity_kg'],
            is_refrigerated=request.POST.get('is_refrigerated') == 'on',
            refrigeration_min_temp=request.POST.get('refrigeration_min_temp') or None,
            refrigeration_max_temp=request.POST.get('refrigeration_max_temp') or None,
            insurance_expiry=request.POST['insurance_expiry'],
            inspection_expiry=request.POST['inspection_expiry'],
            photo=request.FILES.get('photo'),
        )
        messages.success(request, 'Vehicle registered successfully.')
        return redirect('vehicle_list')

    return render(request, 'logistics/vehicle_create.html', {
        'vehicle_types': Vehicle.VEHICLE_TYPES,
    })


@login_required
def route_list_view(request):
    routes = LogisticsRoute.objects.filter(is_active=True)
    cold_only = request.GET.get('cold_chain')
    if cold_only:
        routes = routes.filter(is_cold_chain_available=True)
    return render(request, 'logistics/route_list.html', {'routes': routes})


@login_required
def shipment_list_view(request):
    user = request.user
    if user.role == 'driver':
        shipments = Shipment.objects.filter(driver=user)
    elif user.role == 'farmer':
        shipments = Shipment.objects.filter(order__farmer=user)
    elif user.role == 'buyer':
        shipments = Shipment.objects.filter(order__buyer=user)
    else:
        shipments = Shipment.objects.all()

    return render(request, 'logistics/shipment_list.html', {
        'shipments': shipments.select_related('driver', 'vehicle').order_by('-created_at'),
        'status_choices': Shipment.STATUS_CHOICES,
    })


@login_required
def shipment_detail_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    tracking = ShipmentTracking.objects.filter(shipment=shipment).order_by('timestamp')
    temp_logs = TemperatureLog.objects.filter(shipment=shipment).order_by('-recorded_at')[:20]
    return render(request, 'logistics/shipment_detail.html', {
        'shipment': shipment,
        'tracking': tracking,
        'temp_logs': temp_logs,
    })


@login_required
def shipment_update_status_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk, driver=request.user)
    if request.method == 'POST':
        new_status = request.POST['status']
        shipment.status = new_status
        if new_status == 'picked_up':
            shipment.actual_pickup = timezone.now()
        if new_status == 'delivered':
            shipment.actual_delivery = timezone.now()
            if 'proof_of_delivery_photo' in request.FILES:
                shipment.proof_of_delivery_photo = request.FILES['proof_of_delivery_photo']
        shipment.save()

        # Update GPS location
        ShipmentTracking.objects.create(
            shipment=shipment,
            latitude=request.POST.get('latitude', 0),
            longitude=request.POST.get('longitude', 0),
            speed_kmh=request.POST.get('speed_kmh', 0),
            status_note=f'Status updated to {shipment.get_status_display()}',
        )

        messages.success(request, f'Shipment updated to {shipment.get_status_display()}.')
    return redirect('shipment_detail', pk=pk)


# ============================================================
# ❄️ COLD CHAIN
# ============================================================

@login_required
def cold_storage_list_view(request):
    facilities = ColdStorageFacility.objects.filter(
        is_active=True, status='operational'
    ).select_related('operator')

    min_temp = request.GET.get('min_temp')
    max_temp = request.GET.get('max_temp')
    location = request.GET.get('location')

    if min_temp:
        facilities = facilities.filter(min_temperature_celsius__lte=min_temp)
    if max_temp:
        facilities = facilities.filter(max_temperature_celsius__gte=max_temp)
    if location:
        facilities = facilities.filter(location_name__icontains=location)

    return render(request, 'cold_chain/facility_list.html', {'facilities': facilities})


@login_required
def cold_storage_detail_view(request, pk):
    facility = get_object_or_404(ColdStorageFacility, pk=pk)
    bookings = ColdStorageBooking.objects.filter(
        facility=facility, status__in=['active', 'confirmed']
    ).select_related('booked_by')
    recent_temps = TemperatureLog.objects.filter(
        booking__facility=facility
    ).order_by('-recorded_at')[:30]
    return render(request, 'cold_chain/facility_detail.html', {
        'facility': facility,
        'bookings': bookings,
        'recent_temps': recent_temps,
    })


@login_required
def cold_storage_book_view(request, facility_pk):
    facility = get_object_or_404(ColdStorageFacility, pk=facility_pk, status='operational')

    if request.method == 'POST':
        booking = ColdStorageBooking.objects.create(
            facility=facility,
            booked_by=request.user,
            product_description=request.POST['product_description'],
            quantity_tonnes=request.POST['quantity_tonnes'],
            required_temp_min=request.POST['required_temp_min'],
            required_temp_max=request.POST['required_temp_max'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            notes=request.POST.get('notes', ''),
        )
        Notification.objects.create(
            user=facility.operator,
            notification_type='cold_chain',
            title='New Booking Request',
            message=f'{request.user.get_full_name()} booked {booking.quantity_tonnes}T from {booking.start_date}.',
        )
        messages.success(request, f'Cold storage booked! Total cost: KES {booking.total_cost:,.0f}')
        return redirect('cold_storage_booking_detail', pk=booking.pk)

    return render(request, 'cold_chain/book.html', {'facility': facility})


@login_required
def cold_storage_booking_detail_view(request, pk):
    booking = get_object_or_404(ColdStorageBooking, pk=pk)
    temp_logs = TemperatureLog.objects.filter(booking=booking).order_by('-recorded_at')
    alerts = temp_logs.filter(alert_level__in=['warning', 'critical'])
    return render(request, 'cold_chain/booking_detail.html', {
        'booking': booking,
        'temp_logs': temp_logs[:50],
        'alert_count': alerts.count(),
    })


@login_required
def temperature_log_view(request, booking_pk):
    booking   = get_object_or_404(ColdStorageBooking, pk=booking_pk)
    temp_logs = TemperatureLog.objects.filter(booking=booking).order_by('-recorded_at')
    return render(request, 'cold_chain/temperature_logs.html', {
        'booking': booking,
        'temp_logs': temp_logs,
    })


# ============================================================
# 📊 ANALYTICS
# ============================================================

@login_required
def analytics_dashboard_view(request):
    if request.user.role not in ['admin', 'farmer']:
        messages.error(request, 'Access restricted.')
        return redirect('dashboard')

    last_30 = PlatformMetric.objects.order_by('-date')[:30]
    total_losses = PostHarvestLossReport.objects.aggregate(
        total_kg=Sum('quantity_lost_kg'),
        total_value=Sum('estimated_value_lost'),
    )
    losses_by_cause = PostHarvestLossReport.objects.values('primary_cause').annotate(
        total_kg=Sum('quantity_lost_kg'),
        count=Count('id')
    ).order_by('-total_kg')
    top_markets = MarketPriceIndex.objects.values('market').annotate(
        product_count=Count('product_name', distinct=True)
    )

    return render(request, 'analytics/dashboard.html', {
        'metrics': last_30,
        'total_losses': total_losses,
        'losses_by_cause': losses_by_cause,
        'top_markets': top_markets,
    })


@login_required
def market_prices_view(request):
    market   = request.GET.get('market')
    product  = request.GET.get('product')
    prices   = MarketPriceIndex.objects.order_by('-recorded_date')

    if market:
        prices = prices.filter(market=market)
    if product:
        prices = prices.filter(product_name__icontains=product)

    return render(request, 'analytics/market_prices.html', {
        'prices': prices[:100],
        'markets': MarketPriceIndex.MARKETS,
    })


@login_required
def loss_report_list_view(request):
    if request.user.role == 'farmer':
        reports = PostHarvestLossReport.objects.filter(farm__owner=request.user)
    else:
        reports = PostHarvestLossReport.objects.all()

    return render(request, 'analytics/loss_reports.html', {
        'reports': reports.select_related('farm').order_by('-incident_date'),
        'causes': PostHarvestLossReport.CAUSE_CHOICES,
    })


@login_required
def loss_report_create_view(request):
    farms = Farm.objects.filter(owner=request.user, is_active=True)

    if request.method == 'POST':
        PostHarvestLossReport.objects.create(
            farm=get_object_or_404(Farm, pk=request.POST['farm'], owner=request.user),
            product_name=request.POST['product_name'],
            quantity_lost_kg=request.POST['quantity_lost_kg'],
            estimated_value_lost=request.POST['estimated_value_lost'],
            primary_cause=request.POST['primary_cause'],
            description=request.POST.get('description', ''),
            was_cold_chain_used=request.POST.get('was_cold_chain_used') == 'on',
            incident_date=request.POST['incident_date'],
        )
        messages.success(request, 'Loss report submitted.')
        return redirect('loss_report_list')

    return render(request, 'analytics/loss_report_create.html', {
        'farms': farms,
        'causes': PostHarvestLossReport.CAUSE_CHOICES,
    })


# ============================================================
# 🔔 NOTIFICATIONS
# ============================================================

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def notification_mark_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))


@login_required
def notification_mark_all_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


# ============================================================
# 🌐 API (JSON endpoints for maps / live data)
# ============================================================

@login_required
def api_shipment_location_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    latest = ShipmentTracking.objects.filter(shipment=shipment).order_by('-timestamp').first()
    if not latest:
        return JsonResponse({'error': 'No tracking data'}, status=404)
    return JsonResponse({
        'shipment_code': shipment.shipment_code,
        'status': shipment.status,
        'latitude': float(latest.latitude),
        'longitude': float(latest.longitude),
        'speed_kmh': float(latest.speed_kmh),
        'timestamp': latest.timestamp.isoformat(),
    })


@login_required
def api_temperature_latest_view(request, booking_pk):
    booking = get_object_or_404(ColdStorageBooking, pk=booking_pk)
    latest = TemperatureLog.objects.filter(booking=booking).order_by('-recorded_at').first()
    if not latest:
        return JsonResponse({'error': 'No temperature data'}, status=404)
    return JsonResponse({
        'sensor_id': latest.sensor_id,
        'temperature_celsius': float(latest.temperature_celsius),
        'humidity_percent': float(latest.humidity_percent) if latest.humidity_percent else None,
        'alert_level': latest.alert_level,
        'recorded_at': latest.recorded_at.isoformat(),
    })


@login_required
def api_product_search_view(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(
        status='available',
        name__icontains=q
    ).values('id', 'name', 'price_per_unit', 'unit', 'quantity_available')[:10]
    return JsonResponse({'results': list(products)})


@login_required
def api_market_prices_view(request):
    product = request.GET.get('product', '')
    prices = MarketPriceIndex.objects.filter(
        product_name__icontains=product
    ).order_by('-recorded_date').values(
        'market', 'product_name', 'price_per_kg', 'recorded_date'
    )[:20]
    return JsonResponse({'prices': list(prices)})


@login_required
def api_update_vehicle_location_view(request, vehicle_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, driver=request.user)
    data = json.loads(request.body)
    vehicle.current_latitude  = data.get('latitude')
    vehicle.current_longitude = data.get('longitude')
    vehicle.last_location_update = timezone.now()
    vehicle.save(update_fields=['current_latitude', 'current_longitude', 'last_location_update'])
    return JsonResponse({'status': 'updated'})