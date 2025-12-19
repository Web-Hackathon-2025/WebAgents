"""Seed database with demo data for hackathon presentation."""
import asyncio
import sys
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security.password import hash_password
from app.db.models import (
    Base, User, CustomerProfile, ProviderProfile, Service, ServiceCategory,
    Booking, Review, ProviderAvailability, Notification
)


# Service categories
CATEGORIES = [
    {"name": "Plumbing", "description": "Plumbing and pipe repair services"},
    {"name": "Electrical", "description": "Electrical installation and repair"},
    {"name": "Cleaning", "description": "Home and office cleaning services"},
    {"name": "Carpentry", "description": "Furniture and woodwork services"},
    {"name": "Painting", "description": "House painting and decoration"},
    {"name": "Tutoring", "description": "Academic tutoring services"},
    {"name": "AC Repair", "description": "Air conditioning repair and maintenance"},
    {"name": "Gardening", "description": "Garden maintenance and landscaping"},
]


# Provider data
PROVIDERS = [
    {"name": "Ahmed Khan", "business": "Ahmed's Plumbing", "category": "Plumbing", "phone": "+923001234567", "lat": 24.8607, "lng": 67.0011},
    {"name": "Fatima Ali", "business": "Expert Electricians", "category": "Electrical", "phone": "+923001234568", "lat": 24.8707, "lng": 67.0111},
    {"name": "Hassan Sheikh", "business": "Clean Home Services", "category": "Cleaning", "phone": "+923001234569", "lat": 24.8507, "lng": 67.0211},
    {"name": "Ayesha Malik", "business": "Quality Carpentry", "category": "Carpentry", "phone": "+923001234570", "lat": 24.8807, "lng": 66.9911},
    {"name": "Ali Raza", "business": "Perfect Painters", "category": "Painting", "phone": "+923001234571", "lat": 24.8657, "lng": 67.0051},
    {"name": "Sara Ahmed", "business": "Smart Tutors", "category": "Tutoring", "phone": "+923001234572", "lat": 24.8607, "lng": 67.0311},
    {"name": "Usman Tariq", "business": "Cool AC Repair", "category": "AC Repair", "phone": "+923001234573", "lat": 24.8557, "lng": 67.0111},
    {"name": "Zainab Hassan", "business": "Green Gardens", "category": "Gardening", "phone": "+923001234574", "lat": 24.8707, "lng": 67.0011},
    {"name": "Bilal Ahmed", "business": "Quick Plumbers", "category": "Plumbing", "phone": "+923001234575", "lat": 24.8607, "lng": 66.9911},
    {"name": "Mariam Khan", "business": "Bright Homes Cleaning", "category": "Cleaning", "phone": "+923001234576", "lat": 24.8407, "lng": 67.0111},
    {"name": "Hamza Ali", "business": "Modern Electricals", "category": "Electrical", "phone": "+923001234577", "lat": 24.8707, "lng": 67.0211},
    {"name": "Nida Hussain", "business": "Math Tutors Plus", "category": "Tutoring", "phone": "+923001234578", "lat": 24.8607, "lng": 67.0411},
    {"name": "Kamran Malik", "business": "Wood Works Pro", "category": "Carpentry", "phone": "+923001234579", "lat": 24.8807, "lng": 67.0111},
    {"name": "Hina Amin", "business": "Color Masters", "category": "Painting", "phone": "+923001234580", "lat": 24.8507, "lng": 66.9911},
    {"name": "Tariq Mahmood", "business": "AC Fix Experts", "category": "AC Repair", "phone": "+923001234581", "lat": 24.8657, "lng": 67.0311},
    {"name": "Sana Rafiq", "business": "Garden Care Pro", "category": "Gardening", "phone": "+923001234582", "lat": 24.8707, "lng": 66.9811},
    {"name": "Imran Sheikh", "business": "Pipe Masters", "category": "Plumbing", "phone": "+923001234583", "lat": 24.8357, "lng": 67.0011},
    {"name": "Amber Siddiqui", "business": "Sparkling Clean", "category": "Cleaning", "phone": "+923001234584", "lat": 24.8907, "lng": 67.0111},
    {"name": "Faisal Iqbal", "business": "Power Solutions", "category": "Electrical", "phone": "+923001234585", "lat": 24.8607, "lng": 67.0511},
    {"name": "Rabia Khan", "business": "Learn Easy Tutors", "category": "Tutoring", "phone": "+923001234586", "lat": 24.8457, "lng": 67.0211},
]


async def seed_database():
    """Seed the database with demo data."""
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("🌱 Starting database seeding...")
        
        try:
            # 1. Create service categories
            print("\n📂 Creating service categories...")
            categories_map = {}
            for cat_data in CATEGORIES:
                category = ServiceCategory(
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                db.add(category)
                await db.flush()
                categories_map[cat_data["name"]] = category
                print(f"   ✓ {cat_data['name']}")
            
            await db.commit()
            
            # 2. Create test users
            print("\n👥 Creating test users...")
            
            # Customer test account
            customer_user = User(
                email="customer@test.com",
                password_hash=hash_password("Test@123"),
                phone="+923009876543",
                role="customer",
                is_active=True,
                is_verified=True
            )
            db.add(customer_user)
            await db.flush()
            
            customer_profile = CustomerProfile(
                user_id=customer_user.id,
                full_name="Test Customer",
                address="123 Test Street, Karachi",
                latitude=Decimal("24.8607"),
                longitude=Decimal("67.0011")
            )
            db.add(customer_profile)
            print("   ✓ customer@test.com (Password: Test@123)")
            
            # Provider test account
            provider_user = User(
                email="provider@test.com",
                password_hash=hash_password("Test@123"),
                phone="+923009876544",
                role="provider",
                is_active=True,
                is_verified=True
            )
            db.add(provider_user)
            await db.flush()
            
            provider_profile = ProviderProfile(
                user_id=provider_user.id,
                business_name="Test Provider Services",
                business_type="individual",
                description="Test provider for demo purposes",
                address="456 Provider Avenue, Karachi",
                latitude=Decimal("24.8707"),
                longitude=Decimal("67.0111"),
                is_verified=True,
                verification_status="approved",
                rating=Decimal("4.5"),
                total_reviews=10
            )
            db.add(provider_profile)
            print("   ✓ provider@test.com (Password: Test@123)")
            
            # Admin test account
            admin_user = User(
                email="admin@test.com",
                password_hash=hash_password("Admin@123"),
                phone="+923009876545",
                role="admin",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            print("   ✓ admin@test.com (Password: Admin@123)")
            
            await db.commit()
            
            # 3. Create provider accounts with profiles
            print("\n🏪 Creating provider profiles...")
            providers_list = []
            for i, prov_data in enumerate(PROVIDERS):
                # Create user
                user = User(
                    email=f"provider{i+1}@karigar.com",
                    password_hash=hash_password("Provider@123"),
                    phone=prov_data["phone"],
                    role="provider",
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                await db.flush()
                
                # Create profile
                rating = round(random.uniform(3.5, 5.0), 1)
                profile = ProviderProfile(
                    user_id=user.id,
                    business_name=prov_data["business"],
                    business_type=random.choice(["individual", "company"]),
                    description=f"Professional {prov_data['category'].lower()} services with years of experience.",
                    address=f"{random.randint(1, 999)} Street {random.randint(1, 50)}, Karachi",
                    latitude=Decimal(str(prov_data["lat"])),
                    longitude=Decimal(str(prov_data["lng"])),
                    is_verified=True,
                    verification_status="approved",
                    rating=Decimal(str(rating)),
                    total_reviews=random.randint(5, 50)
                )
                db.add(profile)
                await db.flush()
                providers_list.append((profile, prov_data))
                print(f"   ✓ {prov_data['business']}")
                
            await db.commit()
            
            # 4. Create services for each provider
            print("\n🛠️  Creating services...")
            services_list = []
            for profile, prov_data in providers_list:
                category = categories_map[prov_data["category"]]
                
                # Create 2-4 services per provider
                num_services = random.randint(2, 4)
                service_names = {
                    "Plumbing": ["Pipe Repair", "Drain Cleaning", "Faucet Installation", "Water Heater Repair"],
                    "Electrical": ["Wiring", "Circuit Repair", "Appliance Installation", "Light Fixture Setup"],
                    "Cleaning": ["Deep Cleaning", "Regular Cleaning", "Office Cleaning", "Move-out Cleaning"],
                    "Carpentry": ["Furniture Repair", "Custom Furniture", "Door Installation", "Cabinet Making"],
                    "Painting": ["Interior Painting", "Exterior Painting", "Wall Texture", "Decorative Painting"],
                    "Tutoring": ["Math Tutoring", "English Tutoring", "Science Tutoring", "Test Prep"],
                    "AC Repair": ["AC Servicing", "Gas Refill", "AC Installation", "Compressor Repair"],
                    "Gardening": ["Lawn Mowing", "Plant Care", "Landscaping", "Garden Design"],
                }
                
                available_services = service_names[prov_data["category"]]
                selected_services = random.sample(available_services, min(num_services, len(available_services)))
                
                for service_name in selected_services:
                    base_price = random.randint(500, 5000)
                    service = Service(
                        provider_id=profile.id,
                        category_id=category.id,
                        name=service_name,
                        description=f"Professional {service_name.lower()} service",
                        base_price=Decimal(str(base_price)),
                        price_type="fixed" if random.random() > 0.3 else "hourly",
                        duration_minutes=random.choice([30, 60, 90, 120]),
                        is_available=True
                    )
                    db.add(service)
                    services_list.append(service)
                    
            await db.commit()
            print(f"   ✓ Created {len(services_list)} services")
            
            # 5. Create availability schedules
            print("\n📅 Creating availability schedules...")
            days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for profile, _ in providers_list:
                for day in days_of_week:
                    if random.random() > 0.1:  # 90% chance provider works this day
                        availability = ProviderAvailability(
                            provider_id=profile.id,
                            day_of_week=day,
                            start_time="09:00",
                            end_time="18:00",
                            is_available=True
                        )
                        db.add(availability)
                        
            await db.commit()
            print("   ✓ Availability schedules created")
            
            # 6. Create sample bookings
            print("\n📋 Creating sample bookings...")
            booking_statuses = ["requested", "accepted", "completed", "cancelled"]
            for i in range(20):
                # Random customer and provider
                provider_profile, prov_data = random.choice(providers_list)
                
                # Get a service from this provider
                service = random.choice([s for s in services_list if s.provider_id == provider_profile.id])
                
                status = random.choice(booking_statuses)
                created_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                booking = Booking(
                    customer_id=customer_profile.id,
                    provider_id=provider_profile.id,
                    service_id=service.id,
                    status=status,
                    request_description=f"Need {service.name.lower()} service",
                    service_address="123 Test Street, Karachi",
                    service_latitude=Decimal("24.8607"),
                    service_longitude=Decimal("67.0011"),
                    preferred_date=created_date + timedelta(days=random.randint(1, 7)),
                    quoted_price=service.base_price,
                    final_price=service.base_price if status == "completed" else None,
                    payment_status="paid" if status == "completed" else "pending",
                    ai_match_score=Decimal(str(round(random.uniform(75, 98), 2))),
                    created_at=created_date,
                    completed_at=created_date + timedelta(days=3) if status == "completed" else None
                )
                db.add(booking)
                await db.flush()
                
                # Add reviews for completed bookings
                if status == "completed" and random.random() > 0.3:
                    review = Review(
                        booking_id=booking.id,
                        reviewer_id=customer_profile.user_id,
                        provider_id=provider_profile.id,
                        rating=Decimal(str(random.randint(3, 5))),
                        comment=random.choice([
                            "Excellent service, very professional!",
                            "Good work, would recommend.",
                            "Satisfactory service.",
                            "Great experience, will hire again.",
                            "Quick and efficient work."
                        ]),
                        ai_sentiment_score=Decimal(str(round(random.uniform(0.6, 0.95), 2))),
                        ai_fake_probability=Decimal(str(round(random.uniform(0.05, 0.2), 2)))
                    )
                    db.add(review)
                    
            await db.commit()
            print("   ✓ Sample bookings created")
            
            print("\n✅ Database seeding completed successfully!")
            print("\n📝 Test Accounts:")
            print("   Customer: customer@test.com / Test@123")
            print("   Provider: provider@test.com / Test@123")
            print("   Admin: admin@test.com / Admin@123")
            print(f"\n📊 Created:")
            print(f"   - {len(CATEGORIES)} service categories")
            print(f"   - {len(PROVIDERS) + 3} users")
            print(f"   - {len(services_list)} services")
            print(f"   - 20 sample bookings")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 KARIGAR DATABASE SEEDER")
    print("=" * 60)
    asyncio.run(seed_database())
