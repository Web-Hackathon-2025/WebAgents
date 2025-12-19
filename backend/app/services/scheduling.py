"""Scheduling service using AI scheduling agent."""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.agents.scheduling_agent import SchedulingAgent
from app.db.models import ProviderProfile, ProviderAvailability, ProviderTimeOff, Booking as BookingModel


class SchedulingService:
    """Service for optimal time slot suggestions."""
    
    def __init__(self):
        self.scheduling_agent = SchedulingAgent()
    
    async def get_available_slots(
        self,
        db: AsyncSession,
        provider_id: str,
        preferred_date: Optional[date] = None,
        preferred_time_start: Optional[time] = None,
        preferred_time_end: Optional[time] = None,
        service_duration_minutes: int = 120,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get available time slots for a provider.
        
        Returns suggested slots from scheduling agent.
        """
        # Get provider availability schedule
        availability_result = await db.execute(
            select(ProviderAvailability)
            .where(ProviderAvailability.provider_id == provider_id)
            .where(ProviderAvailability.is_available == True)
        )
        availability = availability_result.scalars().all()
        
        # Get provider's existing bookings
        bookings_result = await db.execute(
            select(BookingModel)
            .where(BookingModel.provider_id == provider_id)
            .where(BookingModel.status.in_(["accepted", "scheduled", "in_progress"]))
        )
        existing_bookings = bookings_result.scalars().all()
        
        # Get provider's time off
        time_off_result = await db.execute(
            select(ProviderTimeOff)
            .where(ProviderTimeOff.provider_id == provider_id)
            .where(
                or_(
                    and_(
                        ProviderTimeOff.start_datetime <= preferred_date,
                        ProviderTimeOff.end_datetime >= preferred_date
                    ) if preferred_date else False,
                    True
                )
            )
        )
        time_off_periods = time_off_result.scalars().all()
        
        # Calculate available slots
        available_slots = self._calculate_available_slots(
            availability,
            existing_bookings,
            time_off_periods,
            preferred_date,
            service_duration_minutes
        )
        
        # Prepare context for scheduling agent
        context = {
            "provider_id": provider_id,
            "preferred_date": preferred_date.isoformat() if preferred_date else None,
            "preferred_time_start": preferred_time_start.isoformat() if preferred_time_start else None,
            "preferred_time_end": preferred_time_end.isoformat() if preferred_time_end else None,
            "service_duration_minutes": service_duration_minutes,
            "available_slots": available_slots,
            "existing_bookings": [
                {
                    "start": b.scheduled_datetime.isoformat() if b.scheduled_datetime else None,
                    "duration": b.estimated_duration_minutes or service_duration_minutes
                }
                for b in existing_bookings
            ],
            "execution_context": "scheduling"
        }
        
        # Execute scheduling agent
        agent_response = await self.scheduling_agent.execute(
            context=context,
            db=db,
            booking_id=booking_id
        )
        
        return agent_response
    
    def _calculate_available_slots(
        self,
        availability: List[ProviderAvailability],
        existing_bookings: List[BookingModel],
        time_off_periods: List[ProviderTimeOff],
        preferred_date: Optional[date],
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Calculate available time slots."""
        slots = []
        
        if not preferred_date:
            return slots
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = preferred_date.weekday()
        
        # Find availability for this day
        day_availability = next(
            (a for a in availability if a.day_of_week == day_of_week),
            None
        )
        
        if not day_availability:
            return slots
        
        # Parse start and end times
        start_time = datetime.strptime(day_availability.start_time, "%H:%M:%S").time()
        end_time = datetime.strptime(day_availability.end_time, "%H:%M:%S").time()
        
        # Generate slots
        current_time = datetime.combine(preferred_date, start_time)
        end_datetime = datetime.combine(preferred_date, end_time)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with existing bookings
            conflicts = False
            for booking in existing_bookings:
                if booking.scheduled_datetime:
                    booking_start = booking.scheduled_datetime
                    booking_end = booking_start + timedelta(
                        minutes=booking.estimated_duration_minutes or duration_minutes
                    )
                    
                    if not (slot_end <= booking_start or current_time >= booking_end):
                        conflicts = True
                        break
            
            # Check if slot conflicts with time off
            if not conflicts:
                for time_off in time_off_periods:
                    if not (slot_end <= time_off.start_datetime or current_time >= time_off.end_datetime):
                        conflicts = True
                        break
            
            if not conflicts:
                slots.append({
                    "start": current_time.isoformat(),
                    "end": slot_end.isoformat()
                })
            
            current_time += timedelta(minutes=30)  # 30-minute increments
        
        return slots

