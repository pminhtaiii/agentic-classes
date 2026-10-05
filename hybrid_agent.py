from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from model import Plan, HybridState
from tools import search_flights, check_seat, book_seat, pay

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

planner_model = model.with_structured_output(Plan)

def planner_node(state: HybridState):
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
    
def replanner_node(state: HybridState):
    request = state.request
    completed_steps = state.plan[:state.current_step]
    
    prompt = f"""
    The current flight booking plan encountered a problem.

    Original request:
    Origin: {request.origin}
    Destination: {request.destination}
    Date: {request.depart_date}
    Latest departure time: {request.latest_departure_time}
    Maximum price: {request.max_price}
    Require refundable: {request.require_refundable}

    Current plan:
    {state.plan}

    Completed steps:
    {completed_steps}

    Current state:
    Selected flight: {state.selected_flight_id}
    Selected seat: {state.selected_seat}
    Booking code: {state.booking_code}

    Problem:
    {state.replan_reason}

    Available actions:
    - search flights
    - check seat availability
    - book a seat
    - pay
    - verify booking

    Create a new plan containing ONLY the remaining actions needed
    from the current state.

    Do not repeat completed actions unless the problem requires it.
    """
    
    new_plan = planner_model.invoke(prompt)
    
    updated_plan = completed_steps + new_plan.steps
    
    return {
        "plan": updated_plan,
        "replan_needed": False,
        "replan_reason": None,
        "replan_count": state.replan_count + 1,
        "status": "replanned"
    }
    
def executor_node(state: HybridState):
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
            if flight["flight_id"] in state.failed_flight_ids:
                continue
            if flight["depart_time"] > request.latest_departure_time:
                continue
            if flight["price"] > request.max_price:
                continue
            if request.require_refundable and not flight["refundable"]:
                continue
            
            valid_flights.append(flight)

        valid_flights.sort(key=lambda flight: flight["price"])
        
        if len(valid_flights) == 0:
            return {
                "replan_needed": True,
                "replan_reason": "No flight satisfies the current constraints",
                "status": "replan_needed"
            }
            
        selected_flight = valid_flights[0]
        
        seat_result = check_seat.invoke({
            "flight_id": selected_flight["flight_id"]
        })
        
        if len(seat_result["available_seats"]) == 0:
            failed_flights = state.failed_flight_ids + [selected_flight["flight_id"]]
            
            return {
                "failed_flight_ids": failed_flights,
                "replan_needed": True,
                "replan_reason": (
                    f"Flight {selected_flight['flight_id']} "
                    "has no available seats."
                ),
                "status": "replan_required"
            }
        return {
            "selected_flight_id": selected_flight["flight_id"],
            "selected_seat": seat_result["available_seats"][0],
            "current_step": state.current_step + 1,
            "status": "executing"
        }
