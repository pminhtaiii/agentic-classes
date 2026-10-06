import json
import time
import uuid

from langchain_core.messages import ToolMessage, HumanMessage
from langgraph.types import Command

from react_agent import react_agent
from plan_execute_agent import plan_execute_graph
from hybrid_agent import hybrid_graph

from harness import VerificationChecker

from mock_data import (
    BOOKINGS,
    FLIGHTS,
    reset_mock_data
)

from human_approved import (
    approve_booking,
    reset_approvals
)


# =========================================================
# SETUP TEST CASE
# =========================================================

def setup_case(case):
    reset_mock_data()
    reset_approvals()

    if case["setup"] == "vj604_no_seat":
        FLIGHTS["VJ604"].available_seats.clear()


# =========================================================
# BUILD USER MESSAGE
# =========================================================

def build_user_message(request):
    return (
        f"Book me a flight from {request.origin} "
        f"to {request.destination} "
        f"on {request.depart_date}, departing before "
        f"{request.latest_departure_time}, "
        f"with a maximum price of {request.max_price} VND. "
        f"Refundable required: {request.require_refundable}."
    )


# =========================================================
# FIND BOOKING CODE FROM REACT MESSAGES
# =========================================================

def find_booking_code(messages):
    for message in reversed(messages):

        if isinstance(message, ToolMessage):
            data = json.loads(message.content)

            if data.get("booking_code"):
                return data["booking_code"]

            if data.get("booking"):
                return data["booking"]["booking_code"]

    return None


# =========================================================
# FIND HUMAN APPROVAL REQUEST FROM REACT
# =========================================================

def find_approval_request(messages):
    for message in reversed(messages):

        if isinstance(message, ToolMessage):
            data = json.loads(message.content)

            if data.get("requires_human_approval") is True:
                return data

    return None


# =========================================================
# BUILD COMMON EVALUATION RESULT
# =========================================================

def build_evaluation_result(
    agent_name,
    case,
    booking_code,
    final_status,
    replan_count,
    latency
):
    booking = BOOKINGS.get(booking_code)

    checker = VerificationChecker(
        case["request"]
    )

    if booking is not None:

        task_completed = checker.is_complete(
            booking
        )

        paid = booking.paid

        selected_flight_id = (
            booking.flight_id
        )

    else:

        task_completed = False
        paid = False
        selected_flight_id = None


    # Agent được xem là xử lý đúng nếu
    # kết quả thực tế giống expected result
    behavior_correct = (
        task_completed
        == case["expected_success"]
    )


    # Kiểm tra permission
    permission_ok = True

    # User không approve nhưng vẫn bị charge
    if (
        case["human_approval"] is False
        and paid is True
    ):
        permission_ok = False


    return {
        "case": case["name"],
        "agent": agent_name,

        "expected_success":
            case["expected_success"],

        "task_completed":
            task_completed,

        "behavior_correct":
            behavior_correct,

        "permission_ok":
            permission_ok,

        "booking_code":
            booking_code,

        "selected_flight_id":
            selected_flight_id,

        "final_status":
            final_status,

        "replan_count":
            replan_count,

        "latency_seconds":
            round(latency, 3)
    }


# =========================================================
# RUN REACT
# =========================================================

def run_react(case):

    setup_case(case)

    request = case["request"]

    user_message = build_user_message(
        request
    )

    start_time = time.perf_counter()


    # -------------------------
    # First ReAct run
    # -------------------------

    result = react_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    })


    booking_code = find_booking_code(
        result["messages"]
    )

    approval_request = (
        find_approval_request(
            result["messages"]
        )
    )


    # -------------------------
    # Human Approval
    # -------------------------

    if approval_request is not None:

        if case["human_approval"] is True:

            approve_booking(
                booking_code
            )

            messages = (
                result["messages"]
                + [
                    HumanMessage(
                        content=(
                            f"I approve payment "
                            f"for booking "
                            f"{booking_code}. "
                            f"Continue the booking "
                            f"and verify its "
                            f"final status."
                        )
                    )
                ]
            )

            result = react_agent.invoke({
                "messages": messages
            })

        else:

            latency = (
                time.perf_counter()
                - start_time
            )

            return build_evaluation_result(
                agent_name="ReAct",
                case=case,
                booking_code=booking_code,
                final_status=
                    "payment_rejected",
                replan_count=0,
                latency=latency
            )


    # -------------------------
    # Final status
    # -------------------------

    latency = (
        time.perf_counter()
        - start_time
    )

    booking = BOOKINGS.get(
        booking_code
    )

    if booking is not None:
        final_status = booking.status
    else:
        final_status = "no_booking"


    return build_evaluation_result(
        agent_name="ReAct",
        case=case,
        booking_code=booking_code,
        final_status=final_status,
        replan_count=0,
        latency=latency
    )


# =========================================================
# RUN PLAN-THEN-EXECUTE
# =========================================================

def run_plan_execute(case):

    setup_case(case)

    start_time = time.perf_counter()


    config = {
        "configurable": {
            "thread_id":
                f"plan-{uuid.uuid4()}"
        }
    }


    # -------------------------
    # Start graph
    # -------------------------

    result = (
        plan_execute_graph.invoke(
            {
                "request":
                    case["request"]
            },
            config=config
        )
    )


    # -------------------------
    # Human Approval
    # -------------------------

    if "__interrupt__" in result:

        result = (
            plan_execute_graph.invoke(
                Command(
                    resume=
                        case[
                            "human_approval"
                        ]
                ),
                config=config
            )
        )


    latency = (
        time.perf_counter()
        - start_time
    )


    return build_evaluation_result(
        agent_name=
            "Plan-then-Execute",

        case=case,

        booking_code=
            result.get(
                "booking_code"
            ),

        final_status=
            result.get(
                "status",
                "unknown"
            ),

        replan_count=0,

        latency=latency
    )


# =========================================================
# RUN HYBRID
# =========================================================

def run_hybrid(case):

    setup_case(case)

    start_time = time.perf_counter()


    config = {
        "configurable": {
            "thread_id":
                f"hybrid-{uuid.uuid4()}"
        }
    }


    # -------------------------
    # Start graph
    # -------------------------

    result = hybrid_graph.invoke(
        {
            "request":
                case["request"]
        },
        config=config
    )


    # -------------------------
    # Human Approval
    # -------------------------

    if "__interrupt__" in result:

        result = hybrid_graph.invoke(
            Command(
                resume=
                    case[
                        "human_approval"
                    ]
            ),
            config=config
        )


    latency = (
        time.perf_counter()
        - start_time
    )


    return build_evaluation_result(
        agent_name="Hybrid",

        case=case,

        booking_code=
            result.get(
                "booking_code"
            ),

        final_status=
            result.get(
                "status",
                "unknown"
            ),

        replan_count=
            result.get(
                "replan_count",
                0
            ),

        latency=latency
    )