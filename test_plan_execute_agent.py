from dotenv import load_dotenv

load_dotenv()

from model import BookingRequest, PlanExecuteState
from plan_execute_agent import planner_node

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

result = planner_node(state)

print(result)

