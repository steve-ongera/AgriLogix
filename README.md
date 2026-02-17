# 🌾 AgriLogix — Logistics in Agriculture Platform

> **Google Tech Summit Presentation Project**
> *Solving post-harvest losses through smart cold chain logistics & direct farm-to-market connections*

---

## 🚨 The Problem

**Post-harvest losses cost Sub-Saharan African farmers 30–40% of their produce** before it even reaches a buyer.

| Root Cause | Impact |
|---|---|
| No refrigerated transport | Produce spoils in transit |
| Middlemen take 40–60% margin | Farmers earn far below market value |
| No real-time tracking | Buyers can't trust delivery timelines |
| Poor road-last-mile connectivity | Small farms are unreachable |
| No cold storage access | Oversupply leads to panic selling at low prices |

---

## 💡 Our Solution: AgriLogix

A **full-stack Django platform** that:
- Connects small-scale farmers **directly** to urban market buyers (zero middlemen)
- Provides **cold chain logistics** with real-time temperature monitoring
- Uses **smart route optimization** to match farms with nearby drivers
- Gives farmers **market intelligence** — know what your produce is worth before you sell
- Tracks **impact metrics** — spoilage prevented, farmer earnings improved, CO₂ saved

---

## 🏗️ System Architecture

```
agrilogix/
├── agrilogix/               # Django project core
│   ├── settings.py          # Configuration
│   └── urls.py              # URL routing
│
├── apps/
│   ├── users/               # 👤 User authentication & roles
│   ├── farmers/             # 🌾 Farm profiles, harvest scheduling
│   ├── products/            # 🥦 Product listings & pricing
│   ├── logistics/           # 🚛 Vehicles, routes, shipment tracking
│   ├── orders/              # 📦 Order lifecycle & payments
│   ├── cold_chain/          # ❄️ Cold storage, temperature monitoring
│   └── analytics/           # 📊 Impact metrics, market prices
│
├── static/                  # CSS, JS, images
├── templates/               # HTML templates
├── media/                   # Uploaded files
├── requirements.txt
└── manage.py
```

---

## 📊 Data Models

### 👤 Users App
| Model | Description |
|---|---|
| `User` | Extended user with roles: Farmer, Buyer, Driver, Cold Storage Operator, Admin |
| `Notification` | In-app alerts for order updates, cold chain alerts, deliveries |

### 🌾 Farmers App
| Model | Description |
|---|---|
| `Farm` | Farm registration with GPS coordinates, infrastructure, certifications |
| `FarmerProfile` | Extended farmer data: payments (M-Pesa), cooperative, earnings tracking |
| `HarvestSchedule` | Planned harvests — enables advance logistics booking |

### 🥦 Products App
| Model | Description |
|---|---|
| `ProductCategory` | Categories with cold chain requirements (e.g., 2–8°C for vegetables) |
| `Product` | Listings: quantity, price, unit, organic/certified flags, expiry tracking |
| `PriceHistory` | Price changes vs. Nairobi wholesale market — market intelligence |

### 🚛 Logistics App
| Model | Description |
|---|---|
| `Vehicle` | Driver vehicles with refrigeration specs, GPS location |
| `LogisticsRoute` | Pre-mapped routes: farm clusters → urban markets, cost per kg |
| `Shipment` | Full shipment lifecycle from pickup to delivery with proof-of-delivery |
| `ShipmentTracking` | Real-time GPS events, speed, timestamps |

### 📦 Orders App
| Model | Description |
|---|---|
| `Order` | Complete order lifecycle with M-Pesa/bank payment integration |
| `OrderItem` | Product line items with cold chain flags |
| `Dispute` | Buyer/farmer dispute resolution system |

### ❄️ Cold Chain App
| Model | Description |
|---|---|
| `ColdStorageFacility` | Registered cold stores with capacity, temperature ranges, costs |
| `ColdStorageBooking` | Booking system with automatic cost calculation |
| `TemperatureLog` | IoT sensor readings with automatic 🟢/🟡/🔴 alert classification |

### 📊 Analytics App
| Model | Description |
|---|---|
| `PostHarvestLossReport` | Tracked losses by cause — measures platform impact |
| `PlatformMetric` | Daily KPIs: GMV, farmer earnings, spoilage prevented |
| `MarketPriceIndex` | Reference prices from Wakulima, Kibuye, Kongowea markets |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/agrilogix.git
cd agrilogix

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser (admin)
python manage.py createsuperuser

# 6. (Optional) Load sample data
python manage.py loaddata fixtures/sample_data.json

# 7. Start development server
python manage.py runserver
```

### Access the Platform
| URL | Description |
|---|---|
| `http://127.0.0.1:8000/admin/` | Admin dashboard |
| `http://127.0.0.1:8000/api/v1/` | REST API root |

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
ALERT_EMAIL=alerts@yourdomain.com
```

---

## 👥 User Roles

| Role | Description |
|---|---|
| 🌾 **Farmer** | Lists produce, schedules harvests, tracks earnings vs middlemen |
| 🏪 **Buyer** | Browses produce, places orders, tracks deliveries |
| 🚛 **Driver** | Accepts shipment assignments, updates GPS location |
| ❄️ **Cold Storage Operator** | Manages facility bookings, monitors temperature sensors |
| ⚙️ **Admin** | Full platform oversight, dispute resolution, analytics |

---

## ❄️ Cold Chain Monitoring

Temperature sensors stream data to `TemperatureLog`. The platform:
- Sets 🟢 Normal when temp is within product range
- Sends 🟡 Warning alerts at ±2°C deviation
- Triggers 🔴 Critical alerts and notifies farmer + buyer if temperature breaks safe range

**Impact:** Reduce spoilage from temperature abuse by **up to 60%**

---

## 📈 Key Impact Metrics (tracked in `PlatformMetric`)

- **Farmer earnings uplift** vs. selling to middlemen
- **Post-harvest losses prevented** (kg and KES value)
- **Cold chain trips** completed
- **Spoilage prevented** (kg tracked by temperature compliance)
- **Market price intelligence** — farmers see Nairobi wholesale prices before negotiating

---

## 🛣️ API Endpoints

| Prefix | Description |
|---|---|
| `/api/v1/auth/` | Registration, login, token auth |
| `/api/v1/farmers/` | Farm profiles, harvest schedules |
| `/api/v1/products/` | Product listings, pricing |
| `/api/v1/logistics/` | Vehicles, routes, shipments, tracking |
| `/api/v1/orders/` | Order creation, payment, disputes |
| `/api/v1/cold-chain/` | Facility bookings, temperature data |
| `/api/v1/analytics/` | Metrics, market prices, loss reports |

---

## 🗺️ Supported Regions (initial launch)

- **Nakuru County → Nairobi** (vegetables, dairy)
- **Kirinyaga/Murang'a → Nairobi** (tea, horticulture)
- **Eldoret → Nairobi** (maize, wheat, dairy)
- **Meru → Nairobi** (miraa, horticulture)

---

## 🔮 Roadmap

- [ ] Mobile app (React Native) for farmers and drivers
- [ ] IoT integration for automated temperature sensor ingestion
- [ ] AI-powered demand forecasting to reduce overproduction
- [ ] Drone/satellite farm monitoring integration
- [ ] M-Pesa Daraja API for live payment processing
- [ ] Multi-language support (Swahili, Kikuyu, Kalenjin)
- [ ] Cooperative group ordering to fill truck capacity

---

## 📖 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Token-based (DRF), extendable to JWT |
| Maps & Routing | Google Maps Platform API |
| Payments | M-Pesa Daraja API (planned) |
| Cold Chain IoT | MQTT → Django signals (planned) |
| Deployment | Docker + Nginx + Gunicorn |

---

## 🤝 Built For

**Google Tech Summit — Logistics in Agriculture Track**

*Empowering the 33 million smallholder farmers in Sub-Saharan Africa with technology they can actually use.*

---

## 📄 License

MIT License — Open for adaptation by agri-tech NGOs and governments.

---

*Made with ❤️ and 🌾 for African agriculture*