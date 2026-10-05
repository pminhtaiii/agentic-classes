from dotenv import load_dotenv

load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from model import Plan, PlanExecuteState
from tools import search_flights, check_seat, book_seat, pay

from harness import PermissionChecker, VerificationChecker
from mock_data import BOOKINGS
from human_approved import is_booking_approved

model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite'
)

permission_checker = PermissionChecker()

planner_model = model.with_structured_output(Plan)

def planner_node(state: PlanExecuteState):
    request = state.request
    prompt = f"""
    Create a plan for completing this flight booking task.

    Request:
    Origin: {request.origin}
    Destination: {request.destination}
    Date: {request.depart_date}
    Latest departure time: {request.latest_departure_time}
    Maximum price: {request.max_price}
    Require refundable: {request.require_refundable}

    Available actions:
    - search flights
    - check seat availability
    - book a seat
    - pay
    - verify booking

    Return only the plan.
    """
    
    plan = planner_model.invoke(prompt)
    
    return {
        "plan": plan.steps,
        "current_step": 0,
        "status": "planned"
    }
    
def executor_node(state: PlanExecuteState):
    current_step = state.plan[state.current_step]
    
    if current_step == "search flights":
        request = state.request
        
        result = search_flights.invoke({
            "origin": request.origin,
            "destination": request.destination,
            "depart_date": request.depart_date
        })

        return {
            "candidate_flights": result["flight"],
            "current_step": state.current_step + 1,
            "status": "executing"
        }
        
    if current_step == "check seat availability":
        request = state.request
        
        valid_flights = []
        
        for flight in state.candidate_flights:
            if flight["depart_time"] > request.latest_departure_time:
                continue
            
            if flight["price"] > request.max_price:
                continue
            
            if request.require_refundable and not flight["refundable"]:
                continue
            
            valid_flights.append(flight)
            
        valid_flights.sort(key=lambda flight: flight["price"])
        
        for flight in valid_flights:
            seat_result = check_seat.invoke({
                "flight_id": flight["flight_id"]
            })
            
            if len(seat_result["available_seats"]) > 0:
                selected_seat = seat_result["available_seats"][0]
                
                return {
                    "selected_flight_id": flight["flight_id"],
                    "selected_seat": selected_seat,
                    "current_step": state.current_step + 1,
                    "status": "executing"
                }
        
        return {
            "status": "no_available_flight"
        }
    
    if current_step == "book a seat":
        result = book_seat.invoke({
            "flight_id": state.selected_flight_id,
            "seat": state.selected_seat
        })
        
        return {
            "booking_code": result["booking"]["booking_code"],
            "current_step": state.current_step + 1,
            "status": "executing"
        }
        
    if current_step == "pay":
        booking = BOOKINGS.get(state.booking_code)
        permission = permission_checker.can_pay(booking)
        
        if (not permission["allowed"] and not is_booking_approved(state.booking_code)):
            return {
                "requires_human_approval": True,
                "status": "waiting_for_approval"
            }
        
        result = pay.invoke({
            "booking_code": state.booking_code
        })
        
        return {
            "requires_human_approval": False,
            "current_step": state.current_step + 1,
            "status": "executing"
        }
        
    if current_step == "verify booking":
        booking = BOOKINGS.get(state.booking_code)
        
        if booking is None:
            return {
            "completed": False,
            "current_step": state.current_step + 1,
            "status": "verification_failed"
            }
            
        checker = VerificationChecker(state.request)
        
        if checker.is_complete(booking):
            return {
                "complete": True,
                "current_step": state.current_step + 1,
                "status": "completed"
            }
            
        return {
            "completed": False,
            "current_step": state.current_step + 1,
            "status": "verification_failed"
        }
