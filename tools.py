import uuid
from langchain.tools import tool
from mock_data import FLIGHTS, BOOKINGS
from model import Booking

@tool
def search_flights(
    origin: str,
    destination: str,
    depart_date: str
) -> dict:
    """
    Search flight by origin, destination and departure date
    """
    matched_flights = []
    
    for flight in FLIGHTS.values():
        if flight.origin == origin and flight.destination == destination and flight.depart_date == depart_date:
            matched_flights.append(flight.model_dump())
            
    return {
        "status": "ok",
        "count": len(matched_flights),
        "flight": matched_flights
    }
    
@tool
def check_seat(flight_id: str) -> dict:
    """
    Check seat availability and flight information
    """
    flight = FLIGHTS.get(flight_id)
    
    if flight is None:
        return {
            "status": "not_found",
            "flight_id": flight_id
        }
        
    return {
        "status": "ok",
        "flight_id": flight.flight_id,
        "price": flight.price,
        "refundable": flight.refundable,
        "available_seats": flight.available_seats
    }
    
@tool
def book_seat(flight_id: str, seat: str) -> dict:
    """
    Reserve a seat on a flight and create a booking
    """
    flight = FLIGHTS.get(flight_id)
    
    if flight is None:
        return {
            "status": "not_found",
            "flight_id": flight_id
        }
        
    if seat not in flight.available_seats:
        return {
            "status": "seat_unavailable",
            "flight_id": flight_id,
            "seat": seat
        }
        
    booking_code = str(uuid.uuid4())[:6].upper()
    
    booking = Booking(
        booking_code=booking_code,
        flight_id=flight.flight_id,
        seat=seat,
        status="held",
        paid=False,
        price=flight.price,
        origin=flight.origin,
        destination=flight.destination,
        depart_date=flight.depart_date,
        depart_time=flight.depart_time,
        refundable=flight.refundable
    )
    
    flight.available_seats.remove(seat)
    
    BOOKINGS[booking_code] = booking
    
    return {
        "status": "held",
        "booking": booking.model_dump()
    }
    
@tool
def pay(booking_code: str) -> dict:
    """
    Pay for a held booking
    """
    booking = BOOKINGS.get(booking_code)
    
    if booking is None:
        return{
            "status": "not_found",
            "booking_code": booking_code
        }
    
    if booking.paid:
        return{
            "status": "already_paid",
            "booking_code": booking_code
        }
        
    booking.paid = True
    booking.status = "confirmed"
    
    return {
        "status": "paid",
        "booking_code": booking_code
    }
    
@tool
def get_booking(booking_code: str) -> dict:
    """
    Get the current booking information
    """
    booking = BOOKINGS.get(booking_code)
    
    if booking is None:
        return {
            "status": "not_found",
            "booking_code": booking_code
        }
        
    return {
        "status": "ok",
        "booking": booking.model_dump()
    }
        
    
    