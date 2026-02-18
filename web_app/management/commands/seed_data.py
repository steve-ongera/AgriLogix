# management/commands/seed_data.py

import random
from datetime import date, timedelta, datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from web_app.models import (
    User, Notification,
    Farm, FarmerProfile, HarvestSchedule,
    ProductCategory, Product, PriceHistory,
    Vehicle, LogisticsRoute, Shipment, ShipmentTracking,
    Order, OrderItem, Dispute,
    ColdStorageFacility, ColdStorageBooking, TemperatureLog,
    PostHarvestLossReport, PlatformMetric, MarketPriceIndex,
)


class Command(BaseCommand):
    help = 'Seed the database with real Kenyan agricultural data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🌱 Seeding AgriLogix with Kenyan data...'))
        self.create_users()
        self.create_farms()
        self.create_farmer_profiles()
        self.create_harvest_schedules()
        self.create_product_categories()
        self.create_products()
        self.create_price_history()
        self.create_vehicles()
        self.create_routes()
        self.create_cold_storage()
        self.create_orders()
        self.create_shipments()
        self.create_cold_storage_bookings()
        self.create_temperature_logs()
        self.create_loss_reports()
        self.create_platform_metrics()
        self.create_market_prices()
        self.create_notifications()
        self.stdout.write(self.style.SUCCESS('✅ Seeding complete!'))

    # ----------------------------------------------------------
    # USERS
    # ----------------------------------------------------------
    def create_users(self):
        self.stdout.write('👤 Creating users...')

        users_data = [
            # Farmers
            {'username': 'kamau_john', 'first_name': 'John', 'last_name': 'Kamau',
             'email': 'jkamau@agri.co.ke', 'phone': '0712345601', 'role': 'farmer',
             'location': 'Nakuru County', 'latitude': -0.3031, 'longitude': 36.0800},
            {'username': 'wanjiku_grace', 'first_name': 'Grace', 'last_name': 'Wanjiku',
             'email': 'gwanjiku@agri.co.ke', 'phone': '0712345602', 'role': 'farmer',
             'location': 'Murang\'a County', 'latitude': -0.7173, 'longitude': 37.1500},
            {'username': 'odhiambo_peter', 'first_name': 'Peter', 'last_name': 'Odhiambo',
             'email': 'podhiambo@agri.co.ke', 'phone': '0712345603', 'role': 'farmer',
             'location': 'Kisumu County', 'latitude': -0.0917, 'longitude': 34.7680},
            {'username': 'muthoni_alice', 'first_name': 'Alice', 'last_name': 'Muthoni',
             'email': 'amuthoni@agri.co.ke', 'phone': '0712345604', 'role': 'farmer',
             'location': 'Kirinyaga County', 'latitude': -0.6590, 'longitude': 37.3300},
            {'username': 'kipkoech_daniel', 'first_name': 'Daniel', 'last_name': 'Kipkoech',
             'email': 'dkipkoech@agri.co.ke', 'phone': '0712345605', 'role': 'farmer',
             'location': 'Uasin Gishu County', 'latitude': 0.5143, 'longitude': 35.2698},
            {'username': 'auma_rose', 'first_name': 'Rose', 'last_name': 'Auma',
             'email': 'rauma@agri.co.ke', 'phone': '0712345606', 'role': 'farmer',
             'location': 'Homa Bay County', 'latitude': -0.5267, 'longitude': 34.4571},
            {'username': 'njoroge_samuel', 'first_name': 'Samuel', 'last_name': 'Njoroge',
             'email': 'snjoroge@agri.co.ke', 'phone': '0712345607', 'role': 'farmer',
             'location': 'Nyeri County', 'latitude': -0.4167, 'longitude': 36.9500},
            {'username': 'chebet_esther', 'first_name': 'Esther', 'last_name': 'Chebet',
             'email': 'echebet@agri.co.ke', 'phone': '0712345608', 'role': 'farmer',
             'location': 'Nandi County', 'latitude': 0.1833, 'longitude': 35.1167},

            # Buyers
            {'username': 'nairobi_fresh_market', 'first_name': 'Nairobi', 'last_name': 'Fresh Market',
             'email': 'orders@nairobifresh.co.ke', 'phone': '0722100001', 'role': 'buyer',
             'location': 'Westlands, Nairobi', 'latitude': -1.2635, 'longitude': 36.8026},
            {'username': 'carrefour_kenya', 'first_name': 'Carrefour', 'last_name': 'Kenya',
             'email': 'produce@carrefour.co.ke', 'phone': '0722100002', 'role': 'buyer',
             'location': 'Two Rivers Mall, Nairobi', 'latitude': -1.2192, 'longitude': 36.8048},
            {'username': 'quickmart_nakuru', 'first_name': 'Quickmart', 'last_name': 'Nakuru',
             'email': 'fresh@quickmart.co.ke', 'phone': '0722100003', 'role': 'buyer',
             'location': 'Nakuru Town', 'latitude': -0.3031, 'longitude': 36.0800},
            {'username': 'mama_mboga_collective', 'first_name': 'Mama Mboga', 'last_name': 'Collective',
             'email': 'collective@mamamboga.co.ke', 'phone': '0722100004', 'role': 'buyer',
             'location': 'Gikomba Market, Nairobi', 'latitude': -1.2833, 'longitude': 36.8453},
            {'username': 'kisumu_wholesale', 'first_name': 'Kisumu', 'last_name': 'Wholesale Hub',
             'email': 'bulk@kisumuwhse.co.ke', 'phone': '0722100005', 'role': 'buyer',
             'location': 'Kibuye Market, Kisumu', 'latitude': -0.1022, 'longitude': 34.7617},

            # Drivers
            {'username': 'mwangi_driver', 'first_name': 'James', 'last_name': 'Mwangi',
             'email': 'jmwangi.driver@agri.co.ke', 'phone': '0733200001', 'role': 'driver',
             'location': 'Nakuru', 'latitude': -0.3031, 'longitude': 36.0800},
            {'username': 'otieno_driver', 'first_name': 'Kevin', 'last_name': 'Otieno',
             'email': 'kotieno.driver@agri.co.ke', 'phone': '0733200002', 'role': 'driver',
             'location': 'Eldoret', 'latitude': 0.5143, 'longitude': 35.2698},
            {'username': 'karanja_driver', 'first_name': 'Michael', 'last_name': 'Karanja',
             'email': 'mkaranja.driver@agri.co.ke', 'phone': '0733200003', 'role': 'driver',
             'location': 'Thika', 'latitude': -1.0332, 'longitude': 37.0693},
            {'username': 'korir_driver', 'first_name': 'Paul', 'last_name': 'Korir',
             'email': 'pkorir.driver@agri.co.ke', 'phone': '0733200004', 'role': 'driver',
             'location': 'Kisumu', 'latitude': -0.0917, 'longitude': 34.7680},

            # Cold Storage Operators
            {'username': 'arctic_cold_kenya', 'first_name': 'Arctic Cold', 'last_name': 'Kenya Ltd',
             'email': 'ops@arcticcold.co.ke', 'phone': '0744300001', 'role': 'cold_storage',
             'location': 'Industrial Area, Nairobi', 'latitude': -1.3031, 'longitude': 36.8516},
            {'username': 'rift_cold_nakuru', 'first_name': 'Rift Valley', 'last_name': 'Cold Stores',
             'email': 'store@riftcold.co.ke', 'phone': '0744300002', 'role': 'cold_storage',
             'location': 'Nakuru', 'latitude': -0.2833, 'longitude': 36.0667},
            {'username': 'lakeside_cold', 'first_name': 'Lakeside', 'last_name': 'Cold Hub',
             'email': 'info@lakesidecold.co.ke', 'phone': '0744300003', 'role': 'cold_storage',
             'location': 'Kisumu', 'latitude': -0.1022, 'longitude': 34.7617},
        ]

        self.users = {}
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'role': data['role'],
                    'location': data['location'],
                    'latitude': Decimal(str(data['latitude'])),
                    'longitude': Decimal(str(data['longitude'])),
                    'is_verified': True,
                    'rating': Decimal(str(round(random.uniform(3.8, 5.0), 2))),
                    'total_transactions': random.randint(10, 200),
                    'password': make_password('agrilogix2024'),
                }
            )
            self.users[data['username']] = user
            if created:
                self.stdout.write(f'  Created user: {user.get_full_name()} ({user.role})')

    # ----------------------------------------------------------
    # FARMS
    # ----------------------------------------------------------
    def create_farms(self):
        self.stdout.write('🌾 Creating farms...')

        farms_data = [
            {'owner': 'kamau_john', 'name': 'Kamau Green Acres', 'farm_type': 'vegetable',
             'description': 'Family-owned vegetable farm producing cabbages, kale and tomatoes for Nairobi markets.',
             'size_acres': 8.5, 'location_name': 'Molo, Nakuru County',
             'latitude': -0.2581, 'longitude': 35.7333, 'nearest_town': 'Molo',
             'distance_to_road_km': 1.2, 'has_storage': False, 'has_electricity': True,
             'water_source': 'Borehole', 'certification': 'Kenya GAP'},
            {'owner': 'wanjiku_grace', 'name': 'Wanjiku Horticulture', 'farm_type': 'fruit',
             'description': 'Specialist mango and avocado farm. Export-quality Hass avocados.',
             'size_acres': 12.0, 'location_name': 'Kandara, Murang\'a County',
             'latitude': -0.8667, 'longitude': 37.0833, 'nearest_town': 'Kandara',
             'distance_to_road_km': 0.5, 'has_storage': True, 'has_electricity': True,
             'water_source': 'River + Irrigation', 'certification': 'GlobalG.A.P'},
            {'owner': 'odhiambo_peter', 'name': 'Odhiambo Mixed Farm', 'farm_type': 'mixed',
             'description': 'Mixed farm growing maize, sorghum, fish pond and free-range chicken.',
             'size_acres': 15.0, 'location_name': 'Nyakach, Kisumu County',
             'latitude': -0.3333, 'longitude': 34.9167, 'nearest_town': 'Ahero',
             'distance_to_road_km': 3.0, 'has_storage': False, 'has_electricity': False,
             'water_source': 'Lake Victoria (Irrigation)', 'certification': ''},
            {'owner': 'muthoni_alice', 'name': 'Alice\'s Tea & Veg Farm', 'farm_type': 'crop',
             'description': 'Tea and French beans for export. Member of Kirinyaga farmers coop.',
             'size_acres': 6.0, 'location_name': 'Kerugoya, Kirinyaga County',
             'latitude': -0.5000, 'longitude': 37.2833, 'nearest_town': 'Kerugoya',
             'distance_to_road_km': 0.8, 'has_storage': False, 'has_electricity': True,
             'water_source': 'Tana River Irrigation', 'certification': 'Rainforest Alliance'},
            {'owner': 'kipkoech_daniel', 'name': 'Kipkoech Grain Farm', 'farm_type': 'crop',
             'description': 'Large-scale maize and wheat production in the breadbasket of Kenya.',
             'size_acres': 45.0, 'location_name': 'Eldoret, Uasin Gishu County',
             'latitude': 0.5200, 'longitude': 35.2700, 'nearest_town': 'Eldoret',
             'distance_to_road_km': 2.5, 'has_storage': True, 'has_electricity': True,
             'water_source': 'Rainfall + Furrow Irrigation', 'certification': 'Kenya GAP'},
            {'owner': 'auma_rose', 'name': 'Rose Lakeside Organics', 'farm_type': 'vegetable',
             'description': 'Organic spinach, onions and sweet potatoes. 100% organic certified.',
             'size_acres': 5.5, 'location_name': 'Kendu Bay, Homa Bay County',
             'latitude': -0.3580, 'longitude': 34.6386, 'nearest_town': 'Kendu Bay',
             'distance_to_road_km': 1.8, 'has_storage': False, 'has_electricity': False,
             'water_source': 'Lake Victoria (Pump)', 'certification': 'Organic Kenya'},
            {'owner': 'njoroge_samuel', 'name': 'Njoroge Coffee & Dairy', 'farm_type': 'mixed',
             'description': 'Arabica coffee and dairy cows. Members of Othaya Farmers Cooperative.',
             'size_acres': 10.0, 'location_name': 'Othaya, Nyeri County',
             'latitude': -0.5667, 'longitude': 36.9667, 'nearest_town': 'Othaya',
             'distance_to_road_km': 1.0, 'has_storage': True, 'has_electricity': True,
             'water_source': 'River Gura', 'certification': 'UTZ Certified'},
            {'owner': 'chebet_esther', 'name': 'Chebet Highland Dairy', 'farm_type': 'dairy',
             'description': 'Friesian dairy cows producing fresh milk for Eldoret and Kisumu markets.',
             'size_acres': 20.0, 'location_name': 'Nandi Hills, Nandi County',
             'latitude': 0.1000, 'longitude': 35.1833, 'nearest_town': 'Nandi Hills',
             'distance_to_road_km': 1.5, 'has_storage': True, 'has_electricity': True,
             'water_source': 'Spring Water', 'certification': 'KDB Certified'},
        ]

        self.farms = {}
        for data in farms_data:
            farm, created = Farm.objects.get_or_create(
                name=data['name'],
                defaults={
                    'owner': self.users[data['owner']],
                    'farm_type': data['farm_type'],
                    'description': data['description'],
                    'size_acres': Decimal(str(data['size_acres'])),
                    'location_name': data['location_name'],
                    'latitude': Decimal(str(data['latitude'])),
                    'longitude': Decimal(str(data['longitude'])),
                    'nearest_town': data['nearest_town'],
                    'distance_to_road_km': Decimal(str(data['distance_to_road_km'])),
                    'has_storage': data['has_storage'],
                    'has_electricity': data['has_electricity'],
                    'water_source': data['water_source'],
                    'certification': data['certification'],
                    'is_active': True,
                }
            )
            self.farms[data['owner']] = farm
            if created:
                self.stdout.write(f'  Created farm: {farm.name}')

    # ----------------------------------------------------------
    # FARMER PROFILES
    # ----------------------------------------------------------
    def create_farmer_profiles(self):
        self.stdout.write('📋 Creating farmer profiles...')

        profiles = [
            {'username': 'kamau_john', 'national_id': '23456781', 'cooperative_name': 'Molo Vegetable Growers Coop',
             'years_experience': 12, 'preferred_payment': 'mpesa', 'mpesa_number': '0712345601',
             'total_sales': 845000, 'savings_vs_middleman': 210000,
             'bio': 'Third-generation farmer. Supplies kale and cabbage to Nairobi supermarkets.'},
            {'username': 'wanjiku_grace', 'national_id': '31234562', 'cooperative_name': 'Kandara Fruit Growers',
             'years_experience': 8, 'preferred_payment': 'mpesa', 'mpesa_number': '0712345602',
             'total_sales': 1200000, 'savings_vs_middleman': 380000,
             'bio': 'Avocado specialist. Exports Hass avocados to Europe via Nairobi agents.'},
            {'username': 'odhiambo_peter', 'national_id': '12345673', 'cooperative_name': 'Nyakach Mixed Farmers',
             'years_experience': 20, 'preferred_payment': 'bank', 'mpesa_number': '0712345603',
             'total_sales': 560000, 'savings_vs_middleman': 130000,
             'bio': 'Pioneer farmer in Nyakach. Practices integrated farming with fish and crops.'},
            {'username': 'muthoni_alice', 'national_id': '28765434', 'cooperative_name': 'Kirinyaga Tea & Hort Coop',
             'years_experience': 15, 'preferred_payment': 'mpesa', 'mpesa_number': '0712345604',
             'total_sales': 720000, 'savings_vs_middleman': 195000,
             'bio': 'French beans exporter and tea farmer. Chairlady of local women farmers group.'},
            {'username': 'kipkoech_daniel', 'national_id': '34512345', 'cooperative_name': 'Uasin Gishu Grain Growers',
             'years_experience': 18, 'preferred_payment': 'bank', 'mpesa_number': '0712345605',
             'total_sales': 3200000, 'savings_vs_middleman': 780000,
             'bio': 'Large-scale maize and wheat farmer. Supplies NCPB and local millers directly.'},
            {'username': 'auma_rose', 'national_id': '19087656', 'cooperative_name': 'Homa Bay Organic Farmers',
             'years_experience': 6, 'preferred_payment': 'mpesa', 'mpesa_number': '0712345606',
             'total_sales': 310000, 'savings_vs_middleman': 95000,
             'bio': 'Organic farming advocate. Trains fellow women in organic practices around Lake Victoria.'},
            {'username': 'njoroge_samuel', 'national_id': '25678907', 'cooperative_name': 'Othaya Farmers Cooperative',
             'years_experience': 22, 'preferred_payment': 'bank', 'mpesa_number': '0712345607',
             'total_sales': 980000, 'savings_vs_middleman': 250000,
             'bio': 'Coffee and dairy farmer in Nyeri highlands. Board member of Othaya Coop.'},
            {'username': 'chebet_esther', 'national_id': '37654328', 'cooperative_name': 'Nandi Dairy Farmers Coop',
             'years_experience': 10, 'preferred_payment': 'mpesa', 'mpesa_number': '0712345608',
             'total_sales': 1450000, 'savings_vs_middleman': 420000,
             'bio': 'Dairy farmer with 30 Friesian cows. Supplies New KCC and local milk vendors.'},
        ]

        for data in profiles:
            FarmerProfile.objects.get_or_create(
                user=self.users[data['username']],
                defaults={
                    'national_id': data['national_id'],
                    'cooperative_name': data['cooperative_name'],
                    'years_experience': data['years_experience'],
                    'preferred_payment': data['preferred_payment'],
                    'mpesa_number': data['mpesa_number'],
                    'total_sales': Decimal(str(data['total_sales'])),
                    'savings_vs_middleman': Decimal(str(data['savings_vs_middleman'])),
                    'bio': data['bio'],
                    'is_premium': data['total_sales'] > 1000000,
                }
            )

    # ----------------------------------------------------------
    # HARVEST SCHEDULES
    # ----------------------------------------------------------
    def create_harvest_schedules(self):
        self.stdout.write('📅 Creating harvest schedules...')

        today = date.today()
        schedules = [
            {'owner': 'kamau_john', 'product_name': 'Cabbages', 'expected_kg': 4500,
             'harvest_date': today + timedelta(days=3), 'pickup_date': today + timedelta(days=5), 'status': 'planned'},
            {'owner': 'kamau_john', 'product_name': 'Kale (Sukuma Wiki)', 'expected_kg': 2000,
             'harvest_date': today + timedelta(days=1), 'pickup_date': today + timedelta(days=2), 'status': 'ready'},
            {'owner': 'wanjiku_grace', 'product_name': 'Hass Avocados', 'expected_kg': 8000,
             'harvest_date': today + timedelta(days=7), 'pickup_date': today + timedelta(days=9), 'status': 'planned'},
            {'owner': 'wanjiku_grace', 'product_name': 'Apple Mangoes', 'expected_kg': 3500,
             'harvest_date': today - timedelta(days=2), 'pickup_date': today, 'status': 'ready'},
            {'owner': 'odhiambo_peter', 'product_name': 'Maize (Dry)', 'expected_kg': 12000,
             'harvest_date': today + timedelta(days=14), 'pickup_date': today + timedelta(days=16), 'status': 'planned'},
            {'owner': 'muthoni_alice', 'product_name': 'French Beans', 'expected_kg': 1800,
             'harvest_date': today + timedelta(days=2), 'pickup_date': today + timedelta(days=3), 'status': 'in_progress'},
            {'owner': 'kipkoech_daniel', 'product_name': 'Wheat', 'expected_kg': 35000,
             'harvest_date': today + timedelta(days=21), 'pickup_date': today + timedelta(days=24), 'status': 'planned'},
            {'owner': 'auma_rose', 'product_name': 'Sweet Potatoes', 'expected_kg': 3000,
             'harvest_date': today + timedelta(days=5), 'pickup_date': today + timedelta(days=6), 'status': 'planned'},
            {'owner': 'njoroge_samuel', 'product_name': 'Arabica Coffee (Parchment)', 'expected_kg': 5000,
             'harvest_date': today + timedelta(days=10), 'pickup_date': today + timedelta(days=12), 'status': 'planned'},
            {'owner': 'chebet_esther', 'product_name': 'Fresh Milk', 'expected_kg': 900,
             'harvest_date': today, 'pickup_date': today, 'status': 'ready'},
        ]

        for data in schedules:
            HarvestSchedule.objects.get_or_create(
                farm=self.farms[data['owner']],
                product_name=data['product_name'],
                harvest_date=data['harvest_date'],
                defaults={
                    'expected_quantity_kg': Decimal(str(data['expected_kg'])),
                    'ready_for_pickup_date': data['pickup_date'],
                    'status': data['status'],
                }
            )

    # ----------------------------------------------------------
    # PRODUCT CATEGORIES
    # ----------------------------------------------------------
    def create_product_categories(self):
        self.stdout.write('🏷️ Creating product categories...')

        categories = [
            {'name': 'Leafy Vegetables', 'icon': '🥬', 'requires_cold_chain': True, 'min_temp': 2, 'max_temp': 8,
             'description': 'Kale, spinach, cabbage, lettuce — highly perishable, cold chain critical.'},
            {'name': 'Root Vegetables', 'icon': '🥕', 'requires_cold_chain': False, 'min_temp': None, 'max_temp': None,
             'description': 'Potatoes, carrots, sweet potatoes, onions, cassava.'},
            {'name': 'Fruits', 'icon': '🥭', 'requires_cold_chain': True, 'min_temp': 8, 'max_temp': 13,
             'description': 'Mangoes, avocados, passion fruit, bananas, pineapples.'},
            {'name': 'Grains & Cereals', 'icon': '🌽', 'requires_cold_chain': False, 'min_temp': None, 'max_temp': None,
             'description': 'Maize, wheat, sorghum, millet, barley.'},
            {'name': 'Legumes', 'icon': '🫘', 'requires_cold_chain': False, 'min_temp': None, 'max_temp': None,
             'description': 'Beans, lentils, peas, cowpeas, groundnuts.'},
            {'name': 'Dairy', 'icon': '🥛', 'requires_cold_chain': True, 'min_temp': 2, 'max_temp': 6,
             'description': 'Fresh milk, fermented milk (mursik), cream. Strict cold chain required.'},
            {'name': 'Cash Crops', 'icon': '☕', 'requires_cold_chain': False, 'min_temp': None, 'max_temp': None,
             'description': 'Coffee, tea, pyrethrum, sunflower, sugarcane.'},
            {'name': 'Herbs & Spices', 'icon': '🌿', 'requires_cold_chain': False, 'min_temp': None, 'max_temp': None,
             'description': 'Coriander, chillies, ginger, turmeric, garlic.'},
            {'name': 'Export Vegetables', 'icon': '🫑', 'requires_cold_chain': True, 'min_temp': 4, 'max_temp': 8,
             'description': 'French beans, snow peas, baby corn, asparagus for export markets.'},
            {'name': 'Poultry & Eggs', 'icon': '🥚', 'requires_cold_chain': True, 'min_temp': 4, 'max_temp': 8,
             'description': 'Free range eggs, chicken. Careful temperature management needed.'},
        ]

        self.categories = {}
        for data in categories:
            cat, _ = ProductCategory.objects.get_or_create(
                name=data['name'],
                defaults={
                    'icon': data['icon'],
                    'requires_cold_chain': data['requires_cold_chain'],
                    'min_temp_celsius': data['min_temp'],
                    'max_temp_celsius': data['max_temp'],
                    'description': data['description'],
                }
            )
            self.categories[data['name']] = cat

    # ----------------------------------------------------------
    # PRODUCTS
    # ----------------------------------------------------------
    def create_products(self):
        self.stdout.write('🥦 Creating products...')

        products_data = [
            {'owner': 'kamau_john', 'category': 'Leafy Vegetables', 'name': 'Cabbages (Drumhead)',
             'variety': 'Drumhead', 'quantity': 4500, 'unit': 'kg', 'price': 25,
             'moq': 100, 'harvest_date': date.today() - timedelta(days=1),
             'expiry_date': date.today() + timedelta(days=7),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Fresh cabbages from Molo highlands. Firm heads, no pesticide residue.'},
            {'owner': 'kamau_john', 'category': 'Leafy Vegetables', 'name': 'Sukuma Wiki (Kale)',
             'variety': 'Collard Greens', 'quantity': 2000, 'unit': 'kg', 'price': 18,
             'moq': 50, 'harvest_date': date.today(),
             'expiry_date': date.today() + timedelta(days=4),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Freshly cut sukuma wiki. Dark green leaves, rich in iron. Nairobi market ready.'},
            {'owner': 'wanjiku_grace', 'category': 'Fruits', 'name': 'Hass Avocados',
             'variety': 'Hass', 'quantity': 8000, 'unit': 'kg', 'price': 85,
             'moq': 500, 'harvest_date': date.today() + timedelta(days=7),
             'expiry_date': date.today() + timedelta(days=21),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Export-grade Hass avocados. GlobalG.A.P certified. Size 16-20. Suitable for EU export.'},
            {'owner': 'wanjiku_grace', 'category': 'Fruits', 'name': 'Apple Mangoes',
             'variety': 'Apple Mango', 'quantity': 3500, 'unit': 'kg', 'price': 55,
             'moq': 200, 'harvest_date': date.today() - timedelta(days=2),
             'expiry_date': date.today() + timedelta(days=10),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Sweet apple mangoes from Kandara. No fibre, rich aroma.'},
            {'owner': 'odhiambo_peter', 'category': 'Grains & Cereals', 'name': 'Dry Maize (WEMA)',
             'variety': 'WEMA Drought Tolerant', 'quantity': 12000, 'unit': 'kg', 'price': 42,
             'moq': 1000, 'harvest_date': date.today() + timedelta(days=14),
             'expiry_date': date.today() + timedelta(days=180),
             'is_organic': False, 'is_certified': False, 'status': 'available',
             'description': 'Drought-tolerant WEMA maize. Moisture content below 13.5%. Milling grade.'},
            {'owner': 'muthoni_alice', 'category': 'Export Vegetables', 'name': 'Fine French Beans',
             'variety': 'Serengeti', 'quantity': 1800, 'unit': 'kg', 'price': 120,
             'moq': 100, 'harvest_date': date.today() + timedelta(days=2),
             'expiry_date': date.today() + timedelta(days=9),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Export-grade fine French beans. Rainforest Alliance certified. Max pod length 12cm.'},
            {'owner': 'kipkoech_daniel', 'category': 'Grains & Cereals', 'name': 'Wheat Grain (EGA Fahari)',
             'variety': 'EGA Fahari', 'quantity': 35000, 'unit': 'kg', 'price': 48,
             'moq': 5000, 'harvest_date': date.today() + timedelta(days=21),
             'expiry_date': date.today() + timedelta(days=365),
             'is_organic': False, 'is_certified': False, 'status': 'available',
             'description': 'High-protein wheat grain. Milling quality. Suitable for Unga and Pembe millers.'},
            {'owner': 'auma_rose', 'category': 'Root Vegetables', 'name': 'Organic Sweet Potatoes',
             'variety': 'Ejumula', 'quantity': 3000, 'unit': 'kg', 'price': 30,
             'moq': 200, 'harvest_date': date.today() + timedelta(days=5),
             'expiry_date': date.today() + timedelta(days=30),
             'is_organic': True, 'is_certified': True, 'status': 'available',
             'description': 'Orange-fleshed sweet potatoes. Organic Kenya certified. Vitamin A rich variety.'},
            {'owner': 'auma_rose', 'category': 'Leafy Vegetables', 'name': 'Organic Spinach',
             'variety': 'Malabar', 'quantity': 800, 'unit': 'kg', 'price': 40,
             'moq': 50, 'harvest_date': date.today() + timedelta(days=1),
             'expiry_date': date.today() + timedelta(days=5),
             'is_organic': True, 'is_certified': True, 'status': 'available',
             'description': 'Organically grown Malabar spinach. Lake Victoria black-cotton soil produce.'},
            {'owner': 'njoroge_samuel', 'category': 'Cash Crops', 'name': 'Arabica Coffee (Parchment)',
             'variety': 'SL28 / SL34', 'quantity': 5000, 'unit': 'kg', 'price': 350,
             'moq': 500, 'harvest_date': date.today() + timedelta(days=10),
             'expiry_date': date.today() + timedelta(days=365),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Nyeri AA-grade Arabica. UTZ certified. Cupping score 86+. Othaya coop processed.'},
            {'owner': 'chebet_esther', 'category': 'Dairy', 'name': 'Fresh Whole Milk',
             'variety': 'Friesian', 'quantity': 900, 'unit': 'litre', 'price': 55,
             'moq': 50, 'harvest_date': date.today(),
             'expiry_date': date.today() + timedelta(days=2),
             'is_organic': False, 'is_certified': True, 'status': 'available',
             'description': 'Fresh whole milk from Friesian cows. KDB certified. Fat content 3.8%.'},
            {'owner': 'chebet_esther', 'category': 'Dairy', 'name': 'Mursik (Fermented Milk)',
             'variety': 'Traditional Nandi', 'quantity': 200, 'unit': 'litre', 'price': 90,
             'moq': 20, 'harvest_date': date.today() - timedelta(days=3),
             'expiry_date': date.today() + timedelta(days=14),
             'is_organic': False, 'is_certified': False, 'status': 'available',
             'description': 'Traditional Nandi mursik fermented in smoked gourd. High demand in Rift Valley.'},
        ]

        self.products = []
        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data['name'],
                farm=self.farms[data['owner']],
                defaults={
                    'category': self.categories[data['category']],
                    'variety': data['variety'],
                    'description': data['description'],
                    'quantity_available': Decimal(str(data['quantity'])),
                    'unit': data['unit'],
                    'price_per_unit': Decimal(str(data['price'])),
                    'minimum_order_quantity': Decimal(str(data['moq'])),
                    'harvest_date': data['harvest_date'],
                    'expiry_date': data['expiry_date'],
                    'is_organic': data['is_organic'],
                    'is_certified': data['is_certified'],
                    'status': data['status'],
                    'views_count': random.randint(20, 500),
                }
            )
            self.products.append(product)
            if created:
                self.stdout.write(f'  Created product: {product.name}')

    # ----------------------------------------------------------
    # PRICE HISTORY
    # ----------------------------------------------------------
    def create_price_history(self):
        self.stdout.write('📈 Creating price history...')

        market_prices = {
            'Cabbages (Drumhead)': [22, 24, 26, 25, 28],
            'Sukuma Wiki (Kale)': [15, 18, 20, 18, 22],
            'Hass Avocados': [70, 78, 85, 90, 95],
            'Apple Mangoes': [45, 50, 55, 60, 58],
            'Fine French Beans': [100, 110, 120, 115, 125],
            'Fresh Whole Milk': [50, 52, 55, 55, 58],
        }

        for product in self.products:
            if product.name in market_prices:
                prices = market_prices[product.name]
                for i, price in enumerate(prices):
                    PriceHistory.objects.get_or_create(
                        product=product,
                        recorded_at__date=date.today() - timedelta(days=(len(prices) - i) * 7),
                        defaults={
                            'price': Decimal(str(price)),
                            'market_price': Decimal(str(price * 1.4)),
                            'notes': f'Week {i+1} price update',
                        }
                    )

    # ----------------------------------------------------------
    # VEHICLES
    # ----------------------------------------------------------
    def create_vehicles(self):
        self.stdout.write('🚛 Creating vehicles...')

        vehicles_data = [
            {'driver': 'mwangi_driver', 'vehicle_type': 'refrigerated', 'plate': 'KDJ 456K',
             'make_model': 'Isuzu NPR Reefer', 'year': 2019, 'capacity_kg': 3000,
             'is_refrigerated': True, 'ref_min': 2, 'ref_max': 8,
             'insurance_expiry': date.today() + timedelta(days=180),
             'inspection_expiry': date.today() + timedelta(days=90),
             'status': 'available',
             'lat': -0.3031, 'lng': 36.0800},
            {'driver': 'otieno_driver', 'vehicle_type': 'truck_medium', 'plate': 'KBC 112G',
             'make_model': 'Mitsubishi Canter', 'year': 2018, 'capacity_kg': 5000,
             'is_refrigerated': False, 'ref_min': None, 'ref_max': None,
             'insurance_expiry': date.today() + timedelta(days=240),
             'inspection_expiry': date.today() + timedelta(days=120),
             'status': 'available',
             'lat': 0.5143, 'lng': 35.2698},
            {'driver': 'karanja_driver', 'vehicle_type': 'truck_small', 'plate': 'KDG 789A',
             'make_model': 'Toyota Dyna', 'year': 2020, 'capacity_kg': 2000,
             'is_refrigerated': False, 'ref_min': None, 'ref_max': None,
             'insurance_expiry': date.today() + timedelta(days=300),
             'inspection_expiry': date.today() + timedelta(days=150),
             'status': 'available',
             'lat': -1.0332, 'lng': 37.0693},
            {'driver': 'korir_driver', 'vehicle_type': 'refrigerated', 'plate': 'KDE 321B',
             'make_model': 'Isuzu ELF Reefer', 'year': 2021, 'capacity_kg': 2500,
             'is_refrigerated': True, 'ref_min': 2, 'ref_max': 10,
             'insurance_expiry': date.today() + timedelta(days=365),
             'inspection_expiry': date.today() + timedelta(days=200),
             'status': 'available',
             'lat': -0.0917, 'lng': 34.7680},
        ]

        self.vehicles = {}
        for data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=data['plate'],
                defaults={
                    'driver': self.users[data['driver']],
                    'vehicle_type': data['vehicle_type'],
                    'make_model': data['make_model'],
                    'year': data['year'],
                    'capacity_kg': Decimal(str(data['capacity_kg'])),
                    'is_refrigerated': data['is_refrigerated'],
                    'refrigeration_min_temp': data['ref_min'],
                    'refrigeration_max_temp': data['ref_max'],
                    'insurance_expiry': data['insurance_expiry'],
                    'inspection_expiry': data['inspection_expiry'],
                    'status': data['status'],
                    'current_latitude': Decimal(str(data['lat'])),
                    'current_longitude': Decimal(str(data['lng'])),
                }
            )
            self.vehicles[data['driver']] = vehicle
            if created:
                self.stdout.write(f'  Created vehicle: {vehicle.plate_number}')

    # ----------------------------------------------------------
    # LOGISTICS ROUTES
    # ----------------------------------------------------------
    def create_routes(self):
        self.stdout.write('🗺️ Creating logistics routes...')

        routes_data = [
            {'name': 'Nakuru → Nairobi (Vegetables)', 'origin': 'Nakuru Town', 'origin_lat': -0.3031,
             'origin_lng': 36.0800, 'dest': 'Wakulima Market, Nairobi', 'dest_lat': -1.2833,
             'dest_lng': 36.8333, 'distance': 157, 'duration': 3.0,
             'cost_per_kg': 3.50, 'cold_chain': True, 'frequency': 'Daily (5AM & 2PM)'},
            {'name': 'Eldoret → Nairobi (Grain)', 'origin': 'Eldoret Town', 'origin_lat': 0.5143,
             'origin_lng': 35.2698, 'dest': 'Industrial Area, Nairobi', 'dest_lat': -1.3031,
             'dest_lng': 36.8516, 'distance': 311, 'duration': 5.5,
             'cost_per_kg': 2.80, 'cold_chain': False, 'frequency': 'Daily'},
            {'name': 'Murang\'a → Nairobi (Fruits)', 'origin': 'Kandara, Murang\'a', 'origin_lat': -0.8667,
             'origin_lng': 37.0833, 'dest': 'Kangemi Market, Nairobi', 'dest_lat': -1.2627,
             'dest_lng': 36.7364, 'distance': 72, 'duration': 2.0,
             'cost_per_kg': 4.20, 'cold_chain': True, 'frequency': 'Daily (6AM)'},
            {'name': 'Kisumu → Nairobi (Produce)', 'origin': 'Kibuye Market, Kisumu', 'origin_lat': -0.1022,
             'origin_lng': 34.7617, 'dest': 'Wakulima Market, Nairobi', 'dest_lat': -1.2833,
             'dest_lng': 36.8333, 'distance': 347, 'duration': 6.0,
             'cost_per_kg': 3.20, 'cold_chain': False, 'frequency': 'Mon/Wed/Fri'},
            {'name': 'Kirinyaga → Nairobi (Export Veg)', 'origin': 'Kerugoya', 'origin_lat': -0.5000,
             'origin_lng': 37.2833, 'dest': 'JKIA Cargo, Nairobi', 'dest_lat': -1.3192,
             'dest_lng': 36.9275, 'distance': 118, 'duration': 2.5,
             'cost_per_kg': 8.00, 'cold_chain': True, 'frequency': 'Daily (4AM for export)'},
            {'name': 'Nandi Hills → Eldoret (Milk)', 'origin': 'Nandi Hills', 'origin_lat': 0.1000,
             'origin_lng': 35.1833, 'dest': 'Eldoret Dairy Hub', 'dest_lat': 0.5200,
             'dest_lng': 35.2700, 'distance': 52, 'duration': 1.2,
             'cost_per_kg': 2.50, 'cold_chain': True, 'frequency': 'Daily (5AM & 3PM)'},
            {'name': 'Nyeri → Nairobi (Coffee)', 'origin': 'Othaya, Nyeri', 'origin_lat': -0.5667,
             'origin_lng': 36.9667, 'dest': 'Nairobi Coffee Exchange', 'dest_lat': -1.2921,
             'dest_lng': 36.8219, 'distance': 143, 'duration': 3.0,
             'cost_per_kg': 5.00, 'cold_chain': False, 'frequency': 'Tue/Thu (Auction days)'},
            {'name': 'Homa Bay → Kisumu (Organics)', 'origin': 'Kendu Bay', 'origin_lat': -0.3580,
             'origin_lng': 34.6386, 'dest': 'Kibuye Market, Kisumu', 'dest_lat': -0.1022,
             'dest_lng': 34.7617, 'distance': 55, 'duration': 1.5,
             'cost_per_kg': 3.80, 'cold_chain': False, 'frequency': 'Mon/Wed/Sat'},
        ]

        self.routes = {}
        for data in routes_data:
            route, created = LogisticsRoute.objects.get_or_create(
                name=data['name'],
                defaults={
                    'origin_name': data['origin'],
                    'origin_latitude': Decimal(str(data['origin_lat'])),
                    'origin_longitude': Decimal(str(data['origin_lng'])),
                    'destination_name': data['dest'],
                    'destination_latitude': Decimal(str(data['dest_lat'])),
                    'destination_longitude': Decimal(str(data['dest_lng'])),
                    'distance_km': Decimal(str(data['distance'])),
                    'estimated_duration_hours': Decimal(str(data['duration'])),
                    'base_cost_per_kg': Decimal(str(data['cost_per_kg'])),
                    'is_cold_chain_available': data['cold_chain'],
                    'frequency': data['frequency'],
                    'is_active': True,
                }
            )
            self.routes[data['name']] = route
            if created:
                self.stdout.write(f'  Created route: {route.name}')

    # ----------------------------------------------------------
    # COLD STORAGE FACILITIES
    # ----------------------------------------------------------
    def create_cold_storage(self):
        self.stdout.write('❄️ Creating cold storage facilities...')

        facilities_data = [
            {'operator': 'arctic_cold_kenya', 'name': 'Arctic Cold Kenya — Nairobi Hub',
             'location': 'Industrial Area, Nairobi', 'lat': -1.3031, 'lng': 36.8516,
             'total_capacity': 500, 'available': 180, 'min_temp': -2, 'max_temp': 8,
             'cost_per_tonne': 850, 'generator': True, 'cert': 'KEBS Certified Cold Chain',
             'status': 'operational'},
            {'operator': 'rift_cold_nakuru', 'name': 'Rift Valley Cold Stores — Nakuru',
             'location': 'Nakuru Town', 'lat': -0.2833, 'lng': 36.0667,
             'total_capacity': 200, 'available': 90, 'min_temp': 2, 'max_temp': 10,
             'cost_per_tonne': 650, 'generator': True, 'cert': 'KEBS Certified',
             'status': 'operational'},
            {'operator': 'lakeside_cold', 'name': 'Lakeside Cold Hub — Kisumu',
             'location': 'Kisumu Port Road', 'lat': -0.1022, 'lng': 34.7617,
             'total_capacity': 150, 'available': 60, 'min_temp': 2, 'max_temp': 12,
             'cost_per_tonne': 700, 'generator': False, 'cert': 'County Health Certified',
             'status': 'operational'},
        ]

        self.facilities = {}
        for data in facilities_data:
            facility, created = ColdStorageFacility.objects.get_or_create(
                name=data['name'],
                defaults={
                    'operator': self.users[data['operator']],
                    'location_name': data['location'],
                    'latitude': Decimal(str(data['lat'])),
                    'longitude': Decimal(str(data['lng'])),
                    'total_capacity_tonnes': Decimal(str(data['total_capacity'])),
                    'available_capacity_tonnes': Decimal(str(data['available'])),
                    'min_temperature_celsius': data['min_temp'],
                    'max_temperature_celsius': data['max_temp'],
                    'cost_per_tonne_per_day': Decimal(str(data['cost_per_tonne'])),
                    'has_backup_generator': data['generator'],
                    'certification': data['cert'],
                    'status': data['status'],
                    'is_active': True,
                }
            )
            self.facilities[data['operator']] = facility
            if created:
                self.stdout.write(f'  Created facility: {facility.name}')

    # ----------------------------------------------------------
    # ORDERS
    # ----------------------------------------------------------
    def create_orders(self):
        self.stdout.write('📦 Creating orders...')

        orders_data = [
            {'number': 'AGL-2024-0001', 'buyer': 'carrefour_kenya', 'farmer': 'kamau_john',
             'product_name': 'Cabbages (Drumhead)', 'qty': 500, 'unit_price': 25,
             'shipping': 3500, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'completed',
             'delivery_addr': 'Two Rivers Mall, Limuru Road, Nairobi',
             'delivery_lat': -1.2192, 'delivery_lng': 36.8048,
             'days_ago': 14},
            {'number': 'AGL-2024-0002', 'buyer': 'nairobi_fresh_market', 'farmer': 'wanjiku_grace',
             'product_name': 'Hass Avocados', 'qty': 1000, 'unit_price': 85,
             'shipping': 8500, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'dispatched',
             'delivery_addr': 'Westlands, Nairobi',
             'delivery_lat': -1.2635, 'delivery_lng': 36.8026,
             'days_ago': 2},
            {'number': 'AGL-2024-0003', 'buyer': 'mama_mboga_collective', 'farmer': 'auma_rose',
             'product_name': 'Organic Spinach', 'qty': 300, 'unit_price': 40,
             'shipping': 2200, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'delivered',
             'delivery_addr': 'Gikomba Market, Nairobi',
             'delivery_lat': -1.2833, 'delivery_lng': 36.8453,
             'days_ago': 5},
            {'number': 'AGL-2024-0004', 'buyer': 'kisumu_wholesale', 'farmer': 'odhiambo_peter',
             'product_name': 'Dry Maize (WEMA)', 'qty': 5000, 'unit_price': 42,
             'shipping': 12000, 'fee_pct': 0.025, 'payment': 'bank', 'status': 'paid',
             'delivery_addr': 'Kibuye Market, Kisumu',
             'delivery_lat': -0.1022, 'delivery_lng': 34.7617,
             'days_ago': 1},
            {'number': 'AGL-2024-0005', 'buyer': 'carrefour_kenya', 'farmer': 'muthoni_alice',
             'product_name': 'Fine French Beans', 'qty': 400, 'unit_price': 120,
             'shipping': 4800, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'confirmed',
             'delivery_addr': 'JKIA Cargo Village, Nairobi',
             'delivery_lat': -1.3192, 'delivery_lng': 36.9275,
             'days_ago': 0},
            {'number': 'AGL-2024-0006', 'buyer': 'quickmart_nakuru', 'farmer': 'chebet_esther',
             'product_name': 'Fresh Whole Milk', 'qty': 200, 'unit_price': 55,
             'shipping': 1500, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'completed',
             'delivery_addr': 'Quickmart Nakuru Branch',
             'delivery_lat': -0.3031, 'delivery_lng': 36.0800,
             'days_ago': 7},
            {'number': 'AGL-2024-0007', 'buyer': 'nairobi_fresh_market', 'farmer': 'kamau_john',
             'product_name': 'Sukuma Wiki (Kale)', 'qty': 600, 'unit_price': 18,
             'shipping': 2800, 'fee_pct': 0.025, 'payment': 'mpesa', 'status': 'pending',
             'delivery_addr': 'Westlands Farmers Market, Nairobi',
             'delivery_lat': -1.2635, 'delivery_lng': 36.8026,
             'days_ago': 0},
            {'number': 'AGL-2024-0008', 'buyer': 'carrefour_kenya', 'farmer': 'njoroge_samuel',
             'product_name': 'Arabica Coffee (Parchment)', 'qty': 1000, 'unit_price': 350,
             'shipping': 9000, 'fee_pct': 0.025, 'payment': 'bank', 'status': 'processing',
             'delivery_addr': 'Nairobi Coffee Exchange, Upper Hill',
             'delivery_lat': -1.2921, 'delivery_lng': 36.8219,
             'days_ago': 3},
        ]

        self.orders = {}
        for data in orders_data:
            subtotal = Decimal(str(data['qty'] * data['unit_price']))
            shipping = Decimal(str(data['shipping']))
            fee = (subtotal * Decimal(str(data['fee_pct']))).quantize(Decimal('0.01'))
            total = subtotal + shipping + fee

            order, created = Order.objects.get_or_create(
                order_number=data['number'],
                defaults={
                    'buyer': self.users[data['buyer']],
                    'farmer': self.users[data['farmer']],
                    'status': data['status'],
                    'subtotal': subtotal,
                    'shipping_cost': shipping,
                    'platform_fee': fee,
                    'total_amount': total,
                    'payment_method': data['payment'],
                    'payment_reference': f'MPESA{random.randint(100000000, 999999999)}' if data['payment'] == 'mpesa' else '',
                    'delivery_address': data['delivery_addr'],
                    'delivery_latitude': Decimal(str(data['delivery_lat'])),
                    'delivery_longitude': Decimal(str(data['delivery_lng'])),
                    'requested_delivery_date': date.today() + timedelta(days=random.randint(1, 3)),
                    'buyer_notes': 'Please ensure produce is fresh and well-packaged.',
                }
            )

            if created:
                # Create order item
                product = next((p for p in self.products if p.name == data['product_name']), None)
                if product:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=Decimal(str(data['qty'])),
                        unit_price=Decimal(str(data['unit_price'])),
                        subtotal=subtotal,
                        requires_cold_chain=product.category.requires_cold_chain if product.category else False,
                    )
                self.stdout.write(f'  Created order: {order.order_number}')
            self.orders[data['number']] = order

    # ----------------------------------------------------------
    # SHIPMENTS
    # ----------------------------------------------------------
    def create_shipments(self):
        self.stdout.write('🚛 Creating shipments...')

        shipment_data = [
            {'code': 'SHP-0001', 'order': 'AGL-2024-0001', 'driver': 'mwangi_driver',
            'route_name': 'Nakuru → Nairobi (Vegetables)',
            'pickup_addr': 'Kamau Green Acres, Molo', 'pickup_lat': -0.2581, 'pickup_lng': 35.7333,
            'delivery_addr': 'Two Rivers Mall, Nairobi', 'delivery_lat': -1.2192, 'delivery_lng': 36.8048,
            'status': 'delivered', 'weight': 500, 'cost': 3500, 'rating': 5, 'days_ago': 14},
            {'code': 'SHP-0002', 'order': 'AGL-2024-0002', 'driver': 'karanja_driver',
            'route_name': "Murang'a → Nairobi (Fruits)",
            'pickup_addr': 'Wanjiku Horticulture, Kandara', 'pickup_lat': -0.8667, 'pickup_lng': 37.0833,
            'delivery_addr': 'Westlands, Nairobi', 'delivery_lat': -1.2635, 'delivery_lng': 36.8026,
            'status': 'in_transit', 'weight': 1000, 'cost': 8500, 'rating': None, 'days_ago': 0},
            {'code': 'SHP-0003', 'order': 'AGL-2024-0003', 'driver': 'karanja_driver',
            'route_name': "Murang'a → Nairobi (Fruits)",
            'pickup_addr': 'Rose Lakeside Organics, Kendu Bay', 'pickup_lat': -0.3580, 'pickup_lng': 34.6386,
            'delivery_addr': 'Gikomba Market, Nairobi', 'delivery_lat': -1.2833, 'delivery_lng': 36.8453,
            'status': 'delivered', 'weight': 300, 'cost': 2200, 'rating': 4, 'days_ago': 5},
            {'code': 'SHP-0006', 'order': 'AGL-2024-0006', 'driver': 'mwangi_driver',
            'route_name': 'Nandi Hills → Eldoret (Milk)',
            'pickup_addr': 'Chebet Highland Dairy, Nandi Hills', 'pickup_lat': 0.1000, 'pickup_lng': 35.1833,
            'delivery_addr': 'Quickmart Nakuru', 'delivery_lat': -0.3031, 'delivery_lng': 36.0800,
            'status': 'delivered', 'weight': 200, 'cost': 1500, 'rating': 5, 'days_ago': 7},
        ]

        self.shipments = {}
        for data in shipment_data:
            if data['order'] not in self.orders:
                continue

            order = self.orders[data['order']]
            route = self.routes.get(data['route_name'])
            vehicle = self.vehicles.get(data['driver'])
            days_ago = data['days_ago']

            # Step 1: Create the Shipment (no 'order' field on Shipment model)
            shipment, created = Shipment.objects.get_or_create(
                shipment_code=data['code'],
                defaults={
                    'driver': self.users[data['driver']],
                    'vehicle': vehicle,
                    'route': route,
                    'pickup_address': data['pickup_addr'],
                    'pickup_latitude': Decimal(str(data['pickup_lat'])),
                    'pickup_longitude': Decimal(str(data['pickup_lng'])),
                    'delivery_address': data['delivery_addr'],
                    'delivery_latitude': Decimal(str(data['delivery_lat'])),
                    'delivery_longitude': Decimal(str(data['delivery_lng'])),
                    'status': data['status'],
                    'scheduled_pickup': datetime.now() - timedelta(days=days_ago),
                    'actual_pickup': datetime.now() - timedelta(days=days_ago, hours=1) if data['status'] != 'pending' else None,
                    'actual_delivery': datetime.now() - timedelta(hours=2) if data['status'] == 'delivered' else None,
                    'shipping_cost': Decimal(str(data['cost'])),
                    'weight_kg': Decimal(str(data['weight'])),
                    'driver_rating': data['rating'],
                }
            )

            # Step 2: Link the shipment back to the Order (Order has the OneToOneField)
            if order.shipment is None:
                order.shipment = shipment
                order.save(update_fields=['shipment'])

            if created:
                # Add tracking events
                for i in range(3):
                    ShipmentTracking.objects.create(
                        shipment=shipment,
                        latitude=Decimal(str(data['pickup_lat'] + (i * 0.1))),
                        longitude=Decimal(str(data['pickup_lng'] + (i * 0.1))),
                        speed_kmh=Decimal(str(round(random.uniform(40, 80), 1))),
                        status_note=['Picked up from farm', 'On highway', 'Approaching destination'][i],
                    )
                self.stdout.write(f'  Created shipment: {shipment.shipment_code}')

            self.shipments[data['code']] = shipment

    # ----------------------------------------------------------
    # COLD STORAGE BOOKINGS
    # ----------------------------------------------------------
    def create_cold_storage_bookings(self):
        self.stdout.write('❄️ Creating cold storage bookings...')

        bookings = [
            {'facility': 'arctic_cold_kenya', 'booked_by': 'wanjiku_grace',
             'order': 'AGL-2024-0002', 'product': 'Hass Avocados',
             'qty_tonnes': 8.0, 'req_min': 8, 'req_max': 13,
             'start': date.today(), 'end': date.today() + timedelta(days=7),
             'status': 'active'},
            {'facility': 'rift_cold_nakuru', 'booked_by': 'chebet_esther',
             'order': 'AGL-2024-0006', 'product': 'Fresh Whole Milk',
             'qty_tonnes': 0.2, 'req_min': 2, 'req_max': 6,
             'start': date.today() - timedelta(days=7), 'end': date.today(),
             'status': 'completed'},
            {'facility': 'arctic_cold_kenya', 'booked_by': 'muthoni_alice',
             'order': 'AGL-2024-0005', 'product': 'Fine French Beans',
             'qty_tonnes': 0.4, 'req_min': 4, 'req_max': 8,
             'start': date.today(), 'end': date.today() + timedelta(days=3),
             'status': 'confirmed'},
            {'facility': 'lakeside_cold', 'booked_by': 'odhiambo_peter',
             'order': None, 'product': 'Tilapia Fish (Buffer Stock)',
             'qty_tonnes': 2.5, 'req_min': -2, 'req_max': 4,
             'start': date.today() - timedelta(days=3), 'end': date.today() + timedelta(days=4),
             'status': 'active'},
        ]

        self.bookings = []
        for data in bookings:
            order = self.orders.get(data['order']) if data['order'] else None
            facility = self.facilities[data['facility']]

            booking, created = ColdStorageBooking.objects.get_or_create(
                facility=facility,
                product_description=data['product'],
                start_date=data['start'],
                defaults={
                    'order': order,
                    'booked_by': self.users[data['booked_by']],
                    'quantity_tonnes': Decimal(str(data['qty_tonnes'])),
                    'required_temp_min': data['req_min'],
                    'required_temp_max': data['req_max'],
                    'end_date': data['end'],
                    'status': data['status'],
                }
            )
            self.bookings.append(booking)
            if created:
                self.stdout.write(f'  Created booking: {booking.product_description} @ {facility.name}')

    # ----------------------------------------------------------
    # TEMPERATURE LOGS
    # ----------------------------------------------------------
    def create_temperature_logs(self):
        self.stdout.write('🌡️ Creating temperature logs...')

        sensor_map = [
            {'booking_idx': 0, 'sensor': 'SNSR-NAI-001', 'temps': [9.2, 9.5, 8.8, 9.1, 10.2, 9.4, 8.9], 'levels': ['normal'] * 6 + ['warning']},
            {'booking_idx': 1, 'sensor': 'SNSR-NAK-001', 'temps': [3.1, 3.4, 2.9, 3.2, 5.8, 7.2, 3.0], 'levels': ['normal'] * 4 + ['warning', 'warning', 'normal']},
            {'booking_idx': 2, 'sensor': 'SNSR-NAI-002', 'temps': [5.1, 5.3, 5.0, 5.2, 5.4, 5.1, 14.3], 'levels': ['normal'] * 6 + ['critical']},
        ]

        for entry in sensor_map:
            if entry['booking_idx'] < len(self.bookings):
                booking = self.bookings[entry['booking_idx']]
                for i, (temp, level) in enumerate(zip(entry['temps'], entry['levels'])):
                    TemperatureLog.objects.create(
                        booking=booking,
                        sensor_id=entry['sensor'],
                        temperature_celsius=Decimal(str(temp)),
                        humidity_percent=Decimal(str(round(random.uniform(85, 95), 1))),
                        alert_level=level,
                        is_alert_sent=(level != 'normal'),
                    )

        # Shipment temperature logs
        if self.shipments:
            shipment = list(self.shipments.values())[0]
            for i, temp in enumerate([6.1, 6.3, 6.8, 7.1, 7.4, 8.9, 6.2]):
                level = 'warning' if temp > 8 else 'normal'
                TemperatureLog.objects.create(
                    shipment=shipment,
                    sensor_id='SNSR-TRUCK-001',
                    temperature_celsius=Decimal(str(temp)),
                    humidity_percent=Decimal(str(round(random.uniform(80, 90), 1))),
                    alert_level=level,
                    is_alert_sent=(level != 'normal'),
                )

        self.stdout.write('  Temperature logs created.')

    # ----------------------------------------------------------
    # POST-HARVEST LOSS REPORTS
    # ----------------------------------------------------------
    def create_loss_reports(self):
        self.stdout.write('📉 Creating post-harvest loss reports...')

        losses = [
            {'owner': 'kamau_john', 'product': 'Cabbages', 'qty_lost': 350, 'value_lost': 8750,
             'cause': 'transport_delay', 'cold_chain': False,
             'date': date.today() - timedelta(days=30),
             'desc': 'Truck broke down on Nakuru-Nairobi highway. Produce sat in heat for 8 hours.'},
            {'owner': 'chebet_esther', 'product': 'Fresh Milk', 'qty_lost': 180, 'value_lost': 9900,
             'cause': 'temperature', 'cold_chain': False,
             'date': date.today() - timedelta(days=45),
             'desc': 'Cold chain failure during transport. Milk curdled before reaching Nakuru.'},
            {'owner': 'odhiambo_peter', 'product': 'Maize', 'qty_lost': 1200, 'value_lost': 50400,
             'cause': 'handling', 'cold_chain': False,
             'date': date.today() - timedelta(days=60),
             'desc': 'Bags torn during loading by middleman. Grain contaminated with moisture.'},
            {'owner': 'wanjiku_grace', 'product': 'Apple Mangoes', 'qty_lost': 400, 'value_lost': 22000,
             'cause': 'road_condition', 'cold_chain': False,
             'date': date.today() - timedelta(days=20),
             'desc': 'Bad murram road to farm caused bruising. 15% of consignment rejected at market.'},
            {'owner': 'muthoni_alice', 'product': 'French Beans', 'qty_lost': 80, 'value_lost': 9600,
             'cause': 'temperature', 'cold_chain': True,
             'date': date.today() - timedelta(days=10),
             'desc': 'Reefer truck temperature spiked to 18°C for 2 hours due to generator fault.'},
            {'owner': 'auma_rose', 'product': 'Organic Spinach', 'qty_lost': 120, 'value_lost': 4800,
             'cause': 'transport_delay', 'cold_chain': False,
             'date': date.today() - timedelta(days=15),
             'desc': 'Ferry delay on Lake Victoria crossing. Spinach wilted by arrival time.'},
        ]

        for data in losses:
            PostHarvestLossReport.objects.get_or_create(
                farm=self.farms[data['owner']],
                product_name=data['product'],
                incident_date=data['date'],
                defaults={
                    'quantity_lost_kg': Decimal(str(data['qty_lost'])),
                    'estimated_value_lost': Decimal(str(data['value_lost'])),
                    'primary_cause': data['cause'],
                    'was_cold_chain_used': data['cold_chain'],
                    'description': data['desc'],
                }
            )

    # ----------------------------------------------------------
    # PLATFORM METRICS
    # ----------------------------------------------------------
    def create_platform_metrics(self):
        self.stdout.write('📊 Creating platform metrics...')

        base_date = date.today() - timedelta(days=30)
        for i in range(30):
            day = base_date + timedelta(days=i)
            PlatformMetric.objects.get_or_create(
                date=day,
                defaults={
                    'total_orders': random.randint(15, 45),
                    'completed_orders': random.randint(10, 38),
                    'total_gmv': Decimal(str(random.randint(180000, 850000))),
                    'total_farmer_earnings': Decimal(str(random.randint(140000, 700000))),
                    'total_middleman_savings': Decimal(str(random.randint(40000, 180000))),
                    'active_farmers': random.randint(12, 28),
                    'active_buyers': random.randint(8, 20),
                    'active_drivers': random.randint(4, 10),
                    'shipments_completed': random.randint(8, 30),
                    'kg_transported': Decimal(str(random.randint(5000, 25000))),
                    'cold_chain_trips': random.randint(2, 10),
                    'spoilage_prevented_kg': Decimal(str(random.randint(200, 1500))),
                    'temperature_alerts_sent': random.randint(0, 5),
                }
            )

    # ----------------------------------------------------------
    # MARKET PRICE INDEX
    # ----------------------------------------------------------
    def create_market_prices(self):
        self.stdout.write('💹 Creating market price index...')

        prices = [
            # Wakulima Market, Nairobi
            ('nairobi_wakulima', 'Cabbage', 35), ('nairobi_wakulima', 'Kale (Sukuma Wiki)', 25),
            ('nairobi_wakulima', 'Tomatoes', 80), ('nairobi_wakulima', 'Onions', 70),
            ('nairobi_wakulima', 'Potatoes', 45), ('nairobi_wakulima', 'Carrots', 50),
            ('nairobi_wakulima', 'Avocado (Hass)', 120), ('nairobi_wakulima', 'Apple Mango', 75),
            ('nairobi_wakulima', 'Banana (Cavendish)', 30), ('nairobi_wakulima', 'Spinach', 55),
            # Kangemi Market
            ('nairobi_kangemi', 'Cabbage', 30), ('nairobi_kangemi', 'Kale (Sukuma Wiki)', 22),
            ('nairobi_kangemi', 'Tomatoes', 75), ('nairobi_kangemi', 'French Beans', 150),
            ('nairobi_kangemi', 'Avocado (Hass)', 115), ('nairobi_kangemi', 'Sweet Potatoes', 40),
            # Kibuye Market, Kisumu
            ('kisumu_kibuye', 'Maize (Dry)', 55), ('kisumu_kibuye', 'Sorghum', 48),
            ('kisumu_kibuye', 'Sweet Potatoes', 35), ('kisumu_kibuye', 'Tilapia (Fresh)', 380),
            ('kisumu_kibuye', 'Spinach', 40), ('kisumu_kibuye', 'Tomatoes', 65),
            # Kongowea Market, Mombasa
            ('mombasa_kongowea', 'Tomatoes', 90), ('mombasa_kongowea', 'Onions', 80),
            ('mombasa_kongowea', 'Cassava', 35), ('mombasa_kongowea', 'Coconut', 25),
            ('mombasa_kongowea', 'Mango (Ngowe)', 60),
            # Central Market, Nakuru
            ('nakuru_central', 'Cabbage', 28), ('nakuru_central', 'Kale (Sukuma Wiki)', 20),
            ('nakuru_central', 'Milk (Fresh)', 60), ('nakuru_central', 'Potatoes', 40),
            ('nakuru_central', 'Wheat Flour', 65),
        ]

        for market, product, price in prices:
            for days_back in [0, 7, 14]:
                MarketPriceIndex.objects.get_or_create(
                    market=market,
                    product_name=product,
                    recorded_date=date.today() - timedelta(days=days_back),
                    defaults={
                        'price_per_kg': Decimal(str(price + random.randint(-5, 5))),
                    }
                )

    # ----------------------------------------------------------
    # NOTIFICATIONS
    # ----------------------------------------------------------
    def create_notifications(self):
        self.stdout.write('🔔 Creating notifications...')

        notifications = [
            {'user': 'kamau_john', 'type': 'order', 'title': 'New Order Received!',
             'message': 'Carrefour Kenya has placed an order for 500kg Cabbages (Order #AGL-2024-0001). Please confirm availability.'},
            {'user': 'wanjiku_grace', 'type': 'cold_chain', 'title': '🌡️ Temperature Warning',
             'message': 'Sensor SNSR-NAI-001 at Arctic Cold Nairobi recorded 10.2°C — slightly above optimal range for your Hass Avocados.'},
            {'user': 'chebet_esther', 'type': 'payment', 'title': '💰 Payment Received',
             'message': 'M-Pesa payment of KES 9,500 received for Order #AGL-2024-0006 (Fresh Milk delivery to Quickmart Nakuru).'},
            {'user': 'mwangi_driver', 'type': 'delivery', 'title': '📦 New Shipment Assigned',
             'message': 'You have been assigned Shipment SHP-0001. Pickup from Kamau Green Acres, Molo at 5:00 AM tomorrow.'},
            {'user': 'nairobi_fresh_market', 'type': 'order', 'title': 'Order Confirmed',
             'message': 'Your order for 1,000kg Hass Avocados from Wanjiku Horticulture has been confirmed. Expected delivery in 2 days.'},
            {'user': 'odhiambo_peter', 'type': 'order', 'title': 'Harvest Ready Reminder',
             'message': 'Your WEMA Maize harvest scheduled for next week. Book your logistics transport now to get the best rate.'},
            {'user': 'muthoni_alice', 'type': 'cold_chain', 'title': '🔴 Critical Temperature Alert!',
             'message': 'URGENT: Sensor SNSR-NAI-002 recorded 14.3°C at Arctic Cold Nairobi. Your French Beans may be at risk. Contact facility immediately.'},
            {'user': 'arctic_cold_kenya', 'type': 'system', 'title': 'Facility Capacity Update',
             'message': 'Your Arctic Cold Nairobi facility is at 64% capacity. 3 new booking requests pending your approval.'},
        ]

        for data in notifications:
            Notification.objects.get_or_create(
                user=self.users[data['user']],
                title=data['title'],
                defaults={
                    'notification_type': data['type'],
                    'message': data['message'],
                    'is_read': random.choice([True, False]),
                }
            )

        self.stdout.write('  Notifications created.')