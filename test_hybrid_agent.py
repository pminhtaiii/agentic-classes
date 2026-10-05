from model import BookingRequest, HybridState
from mock_data import FLIGHTS, reset_mock_data
from hybrid_agent import planner_node, executor_node, replanner_node

reset_mock_data()

FLIGHTS["VJ604"].available_seats.clear()

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

# 1. Planner
plan_result = planner_node(state)

state.plan = plan_result["plan"]
state.current_step = plan_result["current_step"]
state.status = plan_result["status"]

# 2. Search flights
result_1 = executor_node(state)

state.candidate_flights = result_1["candidate_flights"]
state.current_step = result_1["current_step"]
state.status = result_1["status"]

# 3. Check seat
result_2 = executor_node(state)

print("\nBefore replan:")
print(result_2)


# 4. Cập nhật state từ result_2
state.failed_flight_ids = result_2["failed_flight_ids"]
state.replan_needed = result_2["replan_needed"]
state.replan_reason = result_2["replan_reason"]
state.status = result_2["status"]


# 5. Gọi replanner
replan_result = replanner_node(state)

print("\nReplan result:")
print(replan_result)


# 6. Cập nhật state từ replanner
state.plan = replan_result["plan"]
state.replan_needed = replan_result["replan_needed"]
state.replan_reason = replan_result["replan_reason"]
state.replan_count = replan_result["replan_count"]
state.status = replan_result["status"]


# 7. Executor chạy lại sau khi replan
result_3 = executor_node(state)

print("\nAfter replan:")
print(result_3)