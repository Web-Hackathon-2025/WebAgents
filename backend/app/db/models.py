"""SQLAlchemy database models."""
from sqlalchemy import (
    Column, String, Boolean, Integer, DECIMAL, Text, TIMESTAMP, 
    ForeignKey, Enum as SQLEnum, ARRAY, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.db.client import Base


class User(Base):
    """Base user model for all user types."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    role = Column(SQLEnum("customer", "provider", "admin", name="user_role"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(TIMESTAMP)
    
    # Relationships
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)
    provider_profile = relationship("ProviderProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    chat_conversations = relationship("ChatConversation", back_populates="user")


class CustomerProfile(Base):
    """Customer profile information."""
    __tablename__ = "customer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    address = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    location = Column(Geography(geometry_type="POINT", srid=4326))
    city = Column(String(100), index=True)
    postal_code = Column(String(20))
    preferred_language = Column(String(10), default="en")
    notification_preferences = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="customer_profile")
    bookings = relationship("Booking", back_populates="customer", foreign_keys="Booking.customer_id")
    reviews = relationship("Review", back_populates="customer")
    
    __table_args__ = (
        Index("idx_customer_profiles_location", "location", postgresql_using="gist"),
    )


class ProviderProfile(Base):
    """Service provider profile information."""
    __tablename__ = "provider_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    bio = Column(Text)
    profile_image = Column(String(500))
    address = Column(Text)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(20))
    service_radius_km = Column(Integer, default=10, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_documents = Column(JSONB)
    rating_average = Column(DECIMAL(3, 2), default=0.00, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    total_bookings = Column(Integer, default=0, nullable=False)
    completion_rate = Column(DECIMAL(5, 2), default=0.00, nullable=False)
    response_time_minutes = Column(Integer)
    status = Column(
        SQLEnum("pending", "approved", "suspended", "rejected", name="provider_status"),
        default="pending",
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="provider_profile")
    services = relationship("Service", back_populates="provider")
    bookings = relationship("Booking", back_populates="provider", foreign_keys="Booking.provider_id")
    availability = relationship("ProviderAvailability", back_populates="provider")
    time_off = relationship("ProviderTimeOff", back_populates="provider")
    reviews = relationship("Review", back_populates="provider")
    
    __table_args__ = (
        Index("idx_provider_profiles_location", "location", postgresql_using="gist"),
        Index("idx_provider_profiles_rating", "rating_average"),
    )


class ServiceCategory(Base):
    """Service categories."""
    __tablename__ = "service_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(255))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    services = relationship("Service", back_populates="category")


class Service(Base):
    """Service listings by providers."""
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_profiles.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    price_unit = Column(SQLEnum("fixed", "hourly", "daily", name="price_unit"), nullable=False)
    duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    tags = Column(ARRAY(String))
    images = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    provider = relationship("ProviderProfile", back_populates="services")
    category = relationship("ServiceCategory", back_populates="services")
    bookings = relationship("Booking", back_populates="service")
    
    __table_args__ = (
        Index("idx_services_tags", "tags", postgresql_using="gin"),
    )


class Booking(Base):
    """Service requests and bookings."""
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_profiles.id"), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)
    status = Column(
        SQLEnum(
            "requested", "accepted", "scheduled", "in_progress", 
            "completed", "cancelled", "disputed",
            name="booking_status"
        ),
        nullable=False,
        index=True
    )
    request_description = Column(Text, nullable=False)
    service_address = Column(Text, nullable=False)
    service_latitude = Column(DECIMAL(10, 8))
    service_longitude = Column(DECIMAL(11, 8))
    preferred_date = Column(TIMESTAMP)
    preferred_time_start = Column(TIMESTAMP)
    preferred_time_end = Column(TIMESTAMP)
    scheduled_datetime = Column(TIMESTAMP, index=True)
    estimated_duration_minutes = Column(Integer)
    quoted_price = Column(DECIMAL(10, 2))
    final_price = Column(DECIMAL(10, 2))
    payment_status = Column(
        SQLEnum("pending", "paid", "refunded", name="payment_status"),
        default="pending",
        nullable=False
    )
    cancellation_reason = Column(Text)
    cancelled_by = Column(SQLEnum("customer", "provider", "admin", name="cancelled_by"))
    cancelled_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    ai_match_score = Column(DECIMAL(5, 2))
    ai_match_reasoning = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    customer = relationship("CustomerProfile", back_populates="bookings", foreign_keys=[customer_id])
    provider = relationship("ProviderProfile", back_populates="bookings", foreign_keys=[provider_id])
    service = relationship("Service", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)
    dispute = relationship("Dispute", back_populates="booking", uselist=False)


class ProviderAvailability(Base):
    """Provider weekly availability schedule."""
    __tablename__ = "provider_availability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_profiles.id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Sunday, 6=Saturday
    start_time = Column(String(8), nullable=False)  # HH:MM:SS format
    end_time = Column(String(8), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    provider = relationship("ProviderProfile", back_populates="availability")
    
    __table_args__ = (
        Index("idx_provider_availability_day", "provider_id", "day_of_week"),
    )


class ProviderTimeOff(Base):
    """Provider time-off periods."""
    __tablename__ = "provider_time_off"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_profiles.id"), nullable=False, index=True)
    start_datetime = Column(TIMESTAMP, nullable=False, index=True)
    end_datetime = Column(TIMESTAMP, nullable=False, index=True)
    reason = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    provider = relationship("ProviderProfile", back_populates="time_off")
    
    __table_args__ = (
        Index("idx_provider_time_off_dates", "provider_id", "start_datetime", "end_datetime"),
    )


class Review(Base):
    """Reviews and ratings."""
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), unique=True, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_profiles.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False, index=True)  # 1-5
    review_text = Column(Text)
    service_quality = Column(Integer)  # 1-5
    punctuality = Column(Integer)  # 1-5
    professionalism = Column(Integer)  # 1-5
    value_for_money = Column(Integer)  # 1-5
    images = Column(JSONB)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(Text)
    ai_sentiment_score = Column(DECIMAL(3, 2))  # -1 to 1
    ai_quality_score = Column(DECIMAL(3, 2))  # 0 to 1
    provider_response = Column(Text)
    provider_responded_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="review")
    customer = relationship("CustomerProfile", back_populates="reviews")
    provider = relationship("ProviderProfile", back_populates="reviews")


class Notification(Base):
    """User notifications."""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(
        SQLEnum(
            "booking_request", "booking_accepted", "booking_cancelled",
            "review_received", "payment_received", "system",
            name="notification_type"
        ),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class AgentExecutionLog(Base):
    """AI agent execution logs."""
    __tablename__ = "agent_execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(100), nullable=False, index=True)
    execution_context = Column(String(100))  # e.g., 'matching', 'scheduling'
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    execution_time_ms = Column(Integer)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)


class Dispute(Base):
    """Disputes between customers and providers."""
    __tablename__ = "disputes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False, index=True)
    raised_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    dispute_type = Column(
        SQLEnum("service_quality", "pricing", "no_show", "damage", "other", name="dispute_type"),
        nullable=False
    )
    description = Column(Text, nullable=False)
    evidence = Column(JSONB)
    status = Column(
        SQLEnum("open", "under_review", "resolved", "escalated", name="dispute_status"),
        default="open",
        nullable=False,
        index=True
    )
    ai_resolution_suggestion = Column(Text)
    admin_notes = Column(Text)
    resolution = Column(Text)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="dispute")


class ChatConversation(Base):
    """Chat conversation between user and AI assistant."""
    __tablename__ = "chat_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(SQLEnum("customer", "provider", name="user_role"), nullable=False, index=True)
    title = Column(String(255))  # Auto-generated from first message
    session_id = Column(String(255), unique=True, nullable=False, index=True)  # For OpenAI Agents SDK
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """Individual message in a chat conversation."""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chat_conversations.id"), nullable=False, index=True)
    role = Column(SQLEnum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB)  # Store agent handoffs, tool calls, etc.
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")

