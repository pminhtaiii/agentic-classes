from langchain.tools import tool
from mock_data import FLIGHTS

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
    
        
    
    