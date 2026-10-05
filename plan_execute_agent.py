from dotenv import load_dotenv

load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from model import Plan, PlanExecuteState
from tools import search_flights, check_seat

model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite'
)

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
        