from dotenv import load_dotenv

load_dotenv()

from langsmith import traceable
from tools import search_flights, check_seat


@traceable(name="test_mock_tools")
def test_tools():

    search_result = search_flights.invoke({
        "origin": "SGN",
        "destination": "DAD",
        "depart_date": "2026-10-07"
    })

    print("SEARCH:")
    print(search_result)

    seat_result = check_seat.invoke({
        "flight_id": "VN122"
    })

    print("\nCHECK SEAT:")
    print(seat_result)

    return {
        "search": search_result,
        "seat": seat_result
    }


test_tools()