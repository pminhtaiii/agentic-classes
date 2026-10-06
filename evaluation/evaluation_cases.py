from model import BookingRequest


EVALUATION_CASES = [

    # CASE 1
    {
        "name": "normal_booking",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=False
        ),

        "human_approval": True,

        "setup": "normal",

        "expected_success": True
    },


    # CASE 2
    {
        "name": "require_refundable",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=True
        ),

        "human_approval": True,

        "setup": "normal",

        "expected_success": True
    },


    # CASE 3
    {
        "name": "budget_too_low",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=1_000_000,
            require_refundable=False
        ),

        "human_approval": True,

        "setup": "normal",

        "expected_success": False
    },


    # CASE 4
    {
        "name": "no_flight_on_date",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-09",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=False
        ),

        "human_approval": True,

        "setup": "normal",

        "expected_success": False
    },


    # CASE 5
    {
        "name": "payment_rejected",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=False
        ),

        "human_approval": False,

        "setup": "normal",

        "expected_success": False
    },


    # CASE 6
    {
        "name": "best_flight_no_seat",

        "request": BookingRequest(
            origin="SGN",
            destination="DAD",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=False
        ),

        "human_approval": True,

        "setup": "vj604_no_seat",

        "expected_success": True
    },


    # CASE 7
    {
        "name": "different_destination",

        "request": BookingRequest(
            origin="SGN",
            destination="HAN",
            depart_date="2026-10-07",
            latest_departure_time="12:00",
            max_price=2_000_000,
            require_refundable=True
        ),

        "human_approval": True,

        "setup": "normal",

        "expected_success": True
    }
]