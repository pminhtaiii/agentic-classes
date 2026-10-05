from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from model import Plan, HybridState

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
