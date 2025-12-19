"""Geolocation utilities using Google Maps API."""
from typing import Optional, Dict, Any
import googlemaps
from app.core.config import settings


class GeolocationService:
    """Service for geocoding and reverse geocoding."""
    
    def __init__(self):
        self.client = None
        if settings.GOOGLE_MAPS_API_KEY:
            self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Convert address to coordinates."""
        if not self.client:
            return None
        
        try:
            result = self.client.geocode(address)
            if result:
                location = result[0]["geometry"]["location"]
                return {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "formatted_address": result[0].get("formatted_address"),
                    "address_components": result[0].get("address_components", []),
                }
        except Exception:
            return None
        return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Convert coordinates to address."""
        if not self.client:
            return None
        
        try:
            result = self.client.reverse_geocode((latitude, longitude))
            if result:
                return {
                    "formatted_address": result[0].get("formatted_address"),
                    "address_components": result[0].get("address_components", []),
                }
        except Exception:
            return None
        return None


geolocation_service = GeolocationService()

