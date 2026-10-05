from model import BookingRequest, HybridState
from hybrid_agent import planner_node, executor_node


request = BookingRequest(
    origin="SGN",
    destination="DAD",
    depart_date="2026-10-07",
    latest_departure_time="12:00",
    max_price=2_000_000,
    require_refundable=False
)

state = HybridState(
    request=request
)


plan_result = planner_node(state)

state.plan = plan_result["plan"]
state.current_step = plan_result["current_step"]
state.status = plan_result["status"]

result_1 = executor_node(state)

state.candidate_flights = result_1["candidate_flights"]
state.current_step = result_1["current_step"]
state.status = result_1["status"]

result_2 = executor_node(state)

print(result_2)