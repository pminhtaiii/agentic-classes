from langgraph.types import Command

from model import BookingRequest
from hybrid_agent import hybrid_graph
from mock_data import reset_mock_data


reset_mock_data()


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
        "thread_id": "hybrid-test-1"
    }
}


result = hybrid_graph.invoke(
    {
        "request": request
    },
    config=config
)


print("\nResult before approval:")
print(result)

if "__interrupt__" in result:

    approval_info = result["__interrupt__"][0].value

    print("\nPayment requires human approval")
    print("Booking code:", approval_info["booking_code"])
    print("Flight:", approval_info["flight_id"])
    print("Price:", approval_info["price"])
    print("Refundable:", approval_info["refundable"])
    print("Reason:", approval_info["reason"])

    answer = input(
        "\nApprove payment? (yes/no): "
    ).strip().lower()

    if answer == "yes":

        result = hybrid_graph.invoke(
            Command(resume=True),
            config=config
        )

    else:

        result = hybrid_graph.invoke(
            Command(resume=False),
            config=config
        )
        
print("\nFinal result:")
print(result)