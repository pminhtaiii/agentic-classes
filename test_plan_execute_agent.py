from model import BookingRequest
from plan_execute_agent import plan_execute_graph
from mock_data import reset_mock_data
from human_approved import reset_approvals
from langgraph.types import Command

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

config = {
    "configurable": {
        "thread_id": "plan-test-1"
    }
}

result = plan_execute_graph.invoke(
    {
        "request": request
    },
    config=config
)

if "__interrupt__" in result:
    approval_info = result["__interrupt__"][0].value

    print("\nPayment requires approval")
    print("Booking code:", approval_info["booking_code"])
    print("Flight:", approval_info["flight_id"])
    print("Price:", approval_info["price"])
    print("Reason:", approval_info["reason"])

    answer = input("\nApprove payment? (yes/no): ").strip().lower()

    if answer == "yes":
        result = plan_execute_graph.invoke(
            Command(resume=True),
            config=config
        )
    else:
        result = plan_execute_graph.invoke(
            Command(resume=False),
            config=config
        )

print("\nFinal result:")
print(result)