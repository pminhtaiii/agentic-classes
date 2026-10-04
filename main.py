import json

from langchain_core.messages import ToolMessage, HumanMessage

from react_agent import react_agent
from model import BookingRequest, AgentState
from harness import VerificationChecker
from mock_data import BOOKINGS, reset_mock_data
from human_approved import approve_booking, reset_approvals

def find_approval_request(messages):
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            data = json.loads(message.content)
            
            if data.get("requires_human_approval") is True:
                return data
    return None

def find_booking_code(messages):
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            data = json.loads(message.content)
            
            if data.get("booking_code"):
                return data["booking_code"]
            
            if data.get("booking"):
                return data["booking"]["booking_code"]
            
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

state = AgentState(request=request)

user_message = (
    f"Book me a flight from {request.origin} to {request.destination} "
    f"on {request.depart_date}, departing before "
    f"{request.latest_departure_time}, with a maximum price of "
    f"{request.max_price} VND."
)

result = react_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": user_message
        }
    ]
})

booking_code = find_booking_code(result["messages"])

approval_request = find_approval_request(result["messages"])

if approval_request is not None:
    state.requires_human_approval = True
    state.status = "waiting_for_approval"

    print("\nPayment requires human approval.")
    print("Booking code:", booking_code)
    print("Reason:", approval_request["reason"])

    answer = input("\nApprove payment? (yes/no): ").strip().lower()

    if answer == "yes":

        approve_booking(booking_code)
        
        state.requires_human_approval = False
        state.status = "approved"

        messages = result["messages"] + [
            HumanMessage(
                content=(
                    f"I approve payment for booking {booking_code}. "
                    "Continue the booking and verify its final status."
                )
            )
        ]

        result = react_agent.invoke({
            "messages": messages
        })

    else:
        state.status = "payment_rejected"
        print("\nPayment rejected by user.")

checker = VerificationChecker(request)

booking = BOOKINGS.get(booking_code)

if booking is not None and checker.is_complete(booking):
    state.completed = True
    state.status = "completed"
    print("\nVerification passed.")
    print("Task completed successfully.")
else:
    state.completed = False
    state.status = "verification_failed"
    print("\nVerification failed.")
    print("Task is not complete.")

print("\nCurrent Agent State:")
print(state.model_dump())
print("\nAgent:")
print(result["messages"][-1].content)