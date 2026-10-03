from tools import book_seat
from mock_data import FLIGHTS, BOOKINGS

# result = search_flights.invoke({
#     "origin": "SGN",
#     "destination": "DAD",
#     "depart_date": "2026-10-07"
# })
# print(result)

# result = check_seat.invoke({
#     "flight_id": "VN122"
# })
# print(result)

result = book_seat.invoke({
    "flight_id": "VN122",
    "seat": "12A"
})
print(result)
print("\n")
print(FLIGHTS["VN122"].available_seats)