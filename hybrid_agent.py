from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from harness import PermissionChecker, VerificationChecker
from mock_data import BOOKINGS
from model import Plan, HybridState
from tools import search_flights, check_seat, book_seat, pay

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

planner_model = model.with_structured_output(Plan)

permission_checker = PermissionChecker()

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
    
    Rules:
    - Use the exact action names above.
    - Do not rename any action.
    - Start with "search flights".
    - End with "verify booking".

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

    Candidate flights already available:
    {state.candidate_flights}

    Failed flights:
    {state.failed_flight_ids}

    Current state:
    Selected flight: {state.selected_flight_id}
    Selected seat: {state.selected_seat}
    Booking code: {state.booking_code}

    Problem:
    {state.replan_reason}

    You may ONLY use these exact action names:
    - search flights
    - check seat availability
    - book a seat
    - pay
    - verify booking

    Create ONLY the remaining actions needed from the current state.

    Rules:
    - Do not repeat completed actions.
    - Do not rename actions.
    - Do not include "search flights" if candidate flights are already available.
    - Avoid failed flights.
    """

    new_plan = planner_model.invoke(prompt)

    remaining_steps = new_plan.steps

    if state.candidate_flights:
        remaining_steps = [
            step
            for step in remaining_steps
            if step != "search flights"
        ]

    updated_plan = completed_steps + remaining_steps

    return {
        "plan": updated_plan,
        "replan_needed": False,
        "replan_reason": None,
        "replan_count": state.replan_count + 1,
        "status": "replanned"
    }
    
def executor_node(state: HybridState):
    if state.current_step >= len(state.plan):
        return {
            "status": "completed",
            "completed": True
        }
    
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
                "status": "replan_required"
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
        
        if not permission["allowed"]:
            approved = interrupt({
                "booking_code": state.booking_code,
                "flight_id": booking.flight_id,
                "price": booking.price,
                "refundable": booking.refundable,
                "reason": permission["reason"],
                "question": "Do you approve this payment?"
            })
            
            if not approved:
                return {
                    "requires_human_approval": False,
                    "status": "payment_rejected"
                }
                
        pay.invoke({
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
                "completed": True,
                "current_step": state.current_step + 1,
                "status": "completed"
            }

        return {
            "completed": False,
            "current_step": state.current_step + 1,
            "status": "verification_failed"
        }
        
def route_after_executor(state: HybridState):

    if state.replan_needed:
        return "replan"

    if state.status in [
        "completed",
        "verification_failed",
        "payment_rejected",
        "booking_not_found",
        "invalid_plan"
    ]:
        return "stop"

    return "continue"

builder = StateGraph(HybridState)

builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("replanner", replanner_node)

builder.add_edge(START, "planner")
builder.add_edge(
    "planner",
    "executor"
)

builder.add_conditional_edges(
    "executor",
    route_after_executor,
    {
        "continue": "executor",
        "replan": "replanner",
        "stop": END
    }
)

builder.add_edge(
    "replanner",
    "executor"
)

checkpointer = InMemorySaver()
hybrid_graph = builder.compile(
    checkpointer=checkpointer
)
            
                
        
