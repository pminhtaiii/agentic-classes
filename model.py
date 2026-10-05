from pydantic import BaseModel, Field
from typing import Optional

class BookingRequest(BaseModel):
    origin: str
    destination: str
    depart_date: str
    latest_departure_time: str
    max_price: int
    require_refundable: bool = False
    
class Flight(BaseModel):
    flight_id: str
    origin: str
    destination: str
    depart_date: str
    depart_time: str
    price: int
    refundable: bool
    available_seats: list[str]
    
class Booking(BaseModel):
    booking_code: str
    flight_id: str
    seat: str
    status: str
    paid: bool
    price: int
    origin: str
    destination: str
    depart_date: str
    depart_time: str
    refundable: bool
    
class AgentState(BaseModel):
    request: BookingRequest
    selected_flight_id: Optional[str] = None
    selected_seat: Optional[str] = None
    booking_code: Optional[str] = None
    status: str = "started"
    steps: int = 0
    completed: bool = False
    requires_human_approval: bool = False
    last_error: Optional[str] =  False
    
class Plan(BaseModel):
    steps: list[str]
    
class PlanExecuteState(BaseModel):
    request: BookingRequest
    plan: list[str] = []
    current_step: int = 0
    candidate_flights: list[dict] = []
    selected_flight_id: Optional[str] = None
    selected_seat: Optional[str] = None
    booking_code: Optional[str] = None
    status: str = "started"
    completed: bool = False
    requires_human_approval: bool = False
    
class HybridState(BaseModel):
    request: BookingRequest
    plan: list[str] = []
    current_step: int = 0
    candidate_flights: list[dict] = []
    selected_flight_id: Optional[str] = None
    selected_seat: Optional[str] = None
    booking_code: Optional[str] = None
    status: str = "started"
    completed: bool = False
    requires_human_approval: bool = False
    replan_needed: bool = False
    replan_reason: Optional[str] = None
    replan_count: int = 0