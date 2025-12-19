"""Input validation utilities for API requests."""
import re
import math
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
import phonenumbers
from phonenumbers import NumberParseException

from app.core.exceptions import ValidationError


def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """
    Validate geographic coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        Tuple of validated (latitude, longitude)
        
    Raises:
        ValidationError: If coordinates are invalid
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        # Check for NaN or infinity
        if math.isnan(lat) or math.isinf(lat):
            raise ValidationError("Latitude cannot be NaN or infinity")
        if math.isnan(lng) or math.isinf(lng):
            raise ValidationError("Longitude cannot be NaN or infinity")
            
        # Check ranges
        if lat < -90 or lat > 90:
            raise ValidationError(f"Latitude must be between -90 and 90, got {lat}")
        if lng < -180 or lng > 180:
            raise ValidationError(f"Longitude must be between -180 and 180, got {lng}")
            
        return lat, lng
        
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid coordinate values: {str(e)}")


def validate_radius(radius_km: float, max_radius: float = 100.0) -> float:
    """
    Validate search radius.
    
    Args:
        radius_km: Radius in kilometers
        max_radius: Maximum allowed radius
        
    Returns:
        Validated radius
        
    Raises:
        ValidationError: If radius is invalid
    """
    try:
        radius = float(radius_km)
        
        if radius <= 0:
            raise ValidationError(f"Radius must be positive, got {radius}")
        if radius > max_radius:
            raise ValidationError(f"Radius cannot exceed {max_radius}km, got {radius}")
            
        return radius
        
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid radius value: {str(e)}")


def validate_phone(phone_number: str, region: str = "PK") -> str:
    """
    Validate and format phone number.
    
    Args:
        phone_number: Phone number string
        region: ISO country code (default: PK for Pakistan)
        
    Returns:
        Formatted phone number in E164 format
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone_number or not phone_number.strip():
        raise ValidationError("Phone number is required")
        
    try:
        parsed = phonenumbers.parse(phone_number, region)
        
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError(f"Invalid phone number: {phone_number}")
            
        # Return in E164 format (+923001234567)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
    except NumberParseException as e:
        raise ValidationError(f"Invalid phone number format: {str(e)}")


def validate_email(email: str) -> str:
    """
    Validate email address format.
    
    Args:
        email: Email address string
        
    Returns:
        Lowercase email address
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email or not email.strip():
        raise ValidationError("Email is required")
        
    email = email.strip().lower()
    
    # Basic regex validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
        
    # Check length
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email address is too long")
        
    return email


def validate_price(price: Decimal, min_price: Decimal = Decimal("0"), 
                   max_price: Decimal = Decimal("1000000")) -> Decimal:
    """
    Validate price value.
    
    Args:
        price: Price value
        min_price: Minimum allowed price
        max_price: Maximum allowed price
        
    Returns:
        Validated price
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        price = Decimal(str(price))
        
        if price < min_price:
            raise ValidationError(f"Price cannot be less than {min_price}, got {price}")
        if price > max_price:
            raise ValidationError(f"Price cannot exceed {max_price}, got {price}")
            
        # Check decimal places (max 2)
        if price.as_tuple().exponent < -2:
            raise ValidationError("Price cannot have more than 2 decimal places")
            
        return price
        
    except (ValueError, InvalidOperation) as e:
        raise ValidationError(f"Invalid price value: {str(e)}")


def validate_rating(rating: float) -> float:
    """
    Validate rating value.
    
    Args:
        rating: Rating value (0-5)
        
    Returns:
        Validated rating
        
    Raises:
        ValidationError: If rating is invalid
    """
    try:
        rating = float(rating)
        
        if rating < 0 or rating > 5:
            raise ValidationError(f"Rating must be between 0 and 5, got {rating}")
            
        return rating
        
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid rating value: {str(e)}")


def validate_booking_datetime(
    preferred_date: datetime,
    min_advance_hours: int = 2,
    max_advance_days: int = 90
) -> datetime:
    """
    Validate booking date/time.
    
    Args:
        preferred_date: Preferred booking datetime
        min_advance_hours: Minimum hours in advance
        max_advance_days: Maximum days in advance
        
    Returns:
        Validated datetime
        
    Raises:
        ValidationError: If datetime is invalid
    """
    now = datetime.utcnow()
    
    # Check if in the past
    if preferred_date < now:
        raise ValidationError("Booking date cannot be in the past")
        
    # Check minimum advance notice
    min_datetime = now + timedelta(hours=min_advance_hours)
    if preferred_date < min_datetime:
        raise ValidationError(
            f"Booking must be at least {min_advance_hours} hours in advance"
        )
        
    # Check maximum advance booking
    max_datetime = now + timedelta(days=max_advance_days)
    if preferred_date > max_datetime:
        raise ValidationError(
            f"Cannot book more than {max_advance_days} days in advance"
        )
        
    return preferred_date


def validate_text_length(
    text: str,
    field_name: str,
    min_length: int = 0,
    max_length: int = 1000
) -> str:
    """
    Validate text field length.
    
    Args:
        text: Text to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Validated text
        
    Raises:
        ValidationError: If text length is invalid
    """
    if not text:
        text = ""
        
    text = text.strip()
    
    if len(text) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters"
        )
    if len(text) > max_length:
        raise ValidationError(
            f"{field_name} cannot exceed {max_length} characters"
        )
        
    return text


def validate_enum(value: str, allowed_values: list, field_name: str) -> str:
    """
    Validate enum value.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of the field (for error messages)
        
    Returns:
        Validated value
        
    Raises:
        ValidationError: If value is not in allowed list
    """
    if value not in allowed_values:
        raise ValidationError(
            f"Invalid {field_name}. Must be one of: {', '.join(allowed_values)}"
        )
    return value


def sanitize_sql_like(text: str) -> str:
    """
    Sanitize text for SQL LIKE queries.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Escape special LIKE characters
    text = text.replace('\\', '\\\\')
    text = text.replace('%', '\\%')
    text = text.replace('_', '\\_')
    return text


def validate_pagination(page: int = 1, page_size: int = 20, 
                       max_page_size: int = 100) -> Tuple[int, int]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of validated (page, page_size)
        
    Raises:
        ValidationError: If pagination parameters are invalid
    """
    if page < 1:
        raise ValidationError(f"Page must be >= 1, got {page}")
        
    if page_size < 1:
        raise ValidationError(f"Page size must be >= 1, got {page_size}")
        
    if page_size > max_page_size:
        raise ValidationError(
            f"Page size cannot exceed {max_page_size}, got {page_size}"
        )
        
    return page, page_size
