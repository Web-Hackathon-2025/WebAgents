"""Pydantic domain models for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID


# ==================== User Models ====================

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    phone: Optional[str] = None


class UserCreate(UserBase):
    """User registration model."""
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(customer|provider|admin)$")
    
    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """User profile response."""
    id: UUID
    email: EmailStr
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# ==================== Customer Models ====================

class CustomerProfileCreate(BaseModel):
    """Customer profile creation."""
    full_name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_language: str = "en"


class CustomerProfileUpdate(BaseModel):
    """Customer profile update."""
    full_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_language: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class CustomerProfile(BaseModel):
    """Customer profile response."""
    id: UUID
    user_id: UUID
    full_name: str
    address: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    city: Optional[str]
    postal_code: Optional[str]
    preferred_language: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True


# ==================== Provider Models ====================

class ProviderProfileCreate(BaseModel):
    """Provider profile creation."""
    business_name: str = Field(..., min_length=1, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = None
    address: str = Field(..., min_length=1)
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = None
    service_radius_km: int = Field(default=10, ge=1, le=100)


class ProviderProfileUpdate(BaseModel):
    """Provider profile update."""
    business_name: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    service_radius_km: Optional[int] = None
    profile_image: Optional[str] = None


class ProviderProfile(BaseModel):
    """Provider profile response."""
    id: UUID
    user_id: UUID
    business_name: str
    full_name: str
    bio: Optional[str]
    profile_image: Optional[str]
    address: str
    latitude: Decimal
    longitude: Decimal
    city: str
    postal_code: Optional[str]
    service_radius_km: int
    is_verified: bool
    rating_average: Decimal
    rating_count: int
    total_bookings: int
    completion_rate: Decimal
    response_time_minutes: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True


class ProviderAvailabilityCreate(BaseModel):
    """Provider availability creation."""
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$")
    end_time: str = Field(..., pattern="^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$")
    is_available: bool = True


class ProviderAvailability(BaseModel):
    """Provider availability response."""
    id: UUID
    provider_id: UUID
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool
    
    class Config:
        from_attributes = True


class ProviderTimeOffCreate(BaseModel):
    """Provider time-off creation."""
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None


class ProviderTimeOff(BaseModel):
    """Provider time-off response."""
    id: UUID
    provider_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Service Models ====================

class ServiceCategory(BaseModel):
    """Service category response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parent_id: Optional[UUID]
    is_active: bool
    display_order: Optional[int]
    
    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    """Service creation."""
    category_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    base_price: Decimal = Field(..., gt=0)
    price_unit: str = Field(..., pattern="^(fixed|hourly|daily)$")
    duration_minutes: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


class ServiceUpdate(BaseModel):
    """Service update."""
    title: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    price_unit: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


class Service(BaseModel):
    """Service response."""
    id: UUID
    provider_id: UUID
    category_id: UUID
    title: str
    description: str
    base_price: Decimal
    price_unit: str
    duration_minutes: Optional[int]
    is_active: bool
    tags: Optional[List[str]]
    images: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    category: Optional[ServiceCategory] = None
    
    class Config:
        from_attributes = True


# ==================== Booking Models ====================

class BookingRequest(BaseModel):
    """Booking request creation."""
    provider_id: Optional[UUID] = None  # If None, use matching agent
    service_id: UUID
    request_description: str = Field(..., min_length=1)
    service_address: str = Field(..., min_length=1)
    service_latitude: Optional[Decimal] = None
    service_longitude: Optional[Decimal] = None
    preferred_date: Optional[date] = None
    preferred_time_start: Optional[time] = None
    preferred_time_end: Optional[time] = None
    budget: Optional[Decimal] = None


class BookingResponse(BaseModel):
    """Provider booking response."""
    status: str = Field(..., pattern="^(accepted|rejected)$")
    quoted_price: Optional[Decimal] = None
    scheduled_datetime: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class BookingUpdate(BaseModel):
    """Booking status update."""
    status: Optional[str] = None
    scheduled_datetime: Optional[datetime] = None
    final_price: Optional[Decimal] = None
    cancellation_reason: Optional[str] = None


class Booking(BaseModel):
    """Booking response."""
    id: UUID
    customer_id: UUID
    provider_id: UUID
    service_id: UUID
    status: str
    request_description: str
    service_address: str
    service_latitude: Optional[Decimal]
    service_longitude: Optional[Decimal]
    preferred_date: Optional[date]
    preferred_time_start: Optional[time]
    preferred_time_end: Optional[time]
    scheduled_datetime: Optional[datetime]
    estimated_duration_minutes: Optional[int]
    quoted_price: Optional[Decimal]
    final_price: Optional[Decimal]
    payment_status: str
    ai_match_score: Optional[Decimal]
    ai_match_reasoning: Optional[str]
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerProfile] = None
    provider: Optional[ProviderProfile] = None
    service: Optional[Service] = None
    
    class Config:
        from_attributes = True


class BookingTimeline(BaseModel):
    """Booking status timeline."""
    status: str
    timestamp: datetime
    notes: Optional[str] = None


# ==================== Review Models ====================

class ReviewCreate(BaseModel):
    """Review creation."""
    booking_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    service_quality: Optional[int] = Field(None, ge=1, le=5)
    punctuality: Optional[int] = Field(None, ge=1, le=5)
    professionalism: Optional[int] = Field(None, ge=1, le=5)
    value_for_money: Optional[int] = Field(None, ge=1, le=5)
    images: Optional[List[str]] = None


class ReviewUpdate(BaseModel):
    """Review update (provider response)."""
    provider_response: str = Field(..., min_length=1)


class Review(BaseModel):
    """Review response."""
    id: UUID
    booking_id: UUID
    customer_id: UUID
    provider_id: UUID
    rating: int
    review_text: Optional[str]
    service_quality: Optional[int]
    punctuality: Optional[int]
    professionalism: Optional[int]
    value_for_money: Optional[int]
    images: Optional[List[str]]
    is_verified: bool
    is_flagged: bool
    ai_sentiment_score: Optional[Decimal]
    ai_quality_score: Optional[Decimal]
    provider_response: Optional[str]
    provider_responded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerProfile] = None
    
    class Config:
        from_attributes = True


# ==================== Search Models ====================

class SearchFilters(BaseModel):
    """Search filters."""
    category_id: Optional[UUID] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    radius_km: int = Field(default=10, ge=1, le=50)
    min_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    max_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    available_date: Optional[date] = None
    available_time_start: Optional[time] = None
    available_time_end: Optional[time] = None
    city: Optional[str] = None
    tags: Optional[List[str]] = None


class ProviderMatch(BaseModel):
    """Provider match result."""
    provider: ProviderProfile
    match_score: Decimal
    distance_km: Optional[Decimal] = None
    reasoning: Optional[str] = None


class SearchResults(BaseModel):
    """Search results response."""
    providers: List[ProviderMatch]
    total: int
    page: int
    page_size: int


# ==================== Notification Models ====================

class Notification(BaseModel):
    """Notification response."""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Admin Models ====================

class ProviderVerification(BaseModel):
    """Provider verification decision."""
    status: str = Field(..., pattern="^(approved|rejected)$")
    notes: Optional[str] = None


class DisputeCreate(BaseModel):
    """Dispute creation."""
    booking_id: UUID
    dispute_type: str = Field(..., pattern="^(service_quality|pricing|no_show|damage|other)$")
    description: str = Field(..., min_length=1)
    evidence: Optional[List[str]] = None


class DisputeResolution(BaseModel):
    """Dispute resolution."""
    status: str = Field(..., pattern="^(resolved|escalated)$")
    resolution: str = Field(..., min_length=1)
    admin_notes: Optional[str] = None


# ==================== Pagination ====================

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, page_size: int):
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


# ==================== Chat Models ====================

class ChatMessageCreate(BaseModel):
    """Create a new chat message."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None  # If None, creates new conversation


class ChatMessage(BaseModel):
    """Chat message response."""
    id: UUID
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ChatConversation(BaseModel):
    """Chat conversation response."""
    id: UUID
    title: Optional[str]
    session_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str
    conversation_id: UUID
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

