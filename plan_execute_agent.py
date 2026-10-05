from dotenv import load_dotenv

load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from model import Plan, PlanExecuteState

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