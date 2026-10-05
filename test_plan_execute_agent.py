from dotenv import load_dotenv

load_dotenv()

from model import BookingRequest, PlanExecuteState
from plan_execute_agent import planner_node, executor_node
from human_approved import approve_booking

request = BookingRequest(
    origin="SGN",
    destination="DAD",
    depart_date="2026-10-07",
    latest_departure_time="12:00",
    max_price=2_000_000,
    require_refundable=False
)

state = PlanExecuteState(
    request=request
)

plan_result = planner_node(state)

state.plan = plan_result["plan"]
state.current_step = plan_result["current_step"]
state.status = plan_result["status"]

execute_result = executor_node(state)

state.candidate_flights = execute_result["candidate_flights"]
state.current_step = execute_result["current_step"]
state.status = execute_result["status"]

execute_result_2 = executor_node(state)

state.selected_flight_id = execute_result_2["selected_flight_id"]
state.selected_seat = execute_result_2["selected_seat"]
state.current_step = execute_result_2["current_step"]
state.status = execute_result_2["status"]

execute_result_3 = executor_node(state)

state.booking_code = execute_result_3["booking_code"]
state.current_step = execute_result_3["current_step"]
state.status = execute_result_3["status"]

execute_result_4 = executor_node(state)

state.requires_human_approval = execute_result_4["requires_human_approval"]
state.status = execute_result_4["status"]

approve_booking(state.booking_code)

execute_result_4_after_approval = executor_node(state)
print(execute_result_4_after_approval)


