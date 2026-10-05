from model import BookingRequest
from plan_execute_agent import plan_execute_graph
from mock_data import reset_mock_data
from human_approved import reset_approvals


reset_mock_data()
reset_approvals()


request = BookingRequest(
    origin="SGN",
    destination="DAD",
    depart_date="2026-10-07",
    latest_departure_time="12:00",
    max_price=2_000_000,
    require_refundable=False
)


result = plan_execute_graph.invoke({
    "request": request
})


print(result)