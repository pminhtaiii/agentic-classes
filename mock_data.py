from copy import deepcopy
from model import Flight, Booking

INITIAL_FLIGHTS = {
    "VN122": Flight(
        flight_id="VN122",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-07",
        depart_time="08:10",
        price=1_850_000,
        refundable=True,    
        available_seats=["12A", "12B", "14C"]
    ),

    "VJ604": Flight(
        flight_id="VJ604",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-07",
        depart_time="10:20",
        price=1_650_000,
        refundable=False,
        available_seats=["20A", "20B"]
    ),

    "QH118": Flight(
        flight_id="QH118",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-07",
        depart_time="15:40",
        price=1_640_000,
        refundable=True,
        available_seats=["7A", "7B"]
    ),

    "VN134": Flight(
        flight_id="VN134",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-07",
        depart_time="09:30",
        price=2_300_000,
        refundable=True,
        available_seats=["5A", "5B"]
    ),

    "QH120": Flight(
        flight_id="QH120",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-07",
        depart_time="11:15",
        price=1_950_000,
        refundable=True,
        available_seats=[]
    ),

    "VN150": Flight(
        flight_id="VN150",
        origin="SGN",
        destination="DAD",
        depart_date="2026-10-08",
        depart_time="07:30",
        price=1_700_000,
        refundable=True,
        available_seats=["10A", "10B"]
    ),

    "VN210": Flight(
        flight_id="VN210",
        origin="SGN",
        destination="HAN",
        depart_date="2026-10-07",
        depart_time="09:00",
        price=1_900_000,
        refundable=True,
        available_seats=["15A", "15B"]
    )
}

FLIGHTS = deepcopy(INITIAL_FLIGHTS)

BOOKINGS: dict[str, Booking] = {}

def reset_mock_data():
    """
    Reset the mock data to the beginning state
    """
    FLIGHTS.clear()
    BOOKINGS.clear()
    FLIGHTS.update(deepcopy(INITIAL_FLIGHTS))