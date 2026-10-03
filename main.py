from tools import search_flights, check_seat

# result = search_flights.invoke({
#     "origin": "SGN",
#     "destination": "DAD",
#     "depart_date": "2026-10-07"
# })

# print(result)

result = check_seat.invoke({
    "flight_id": "VN122"
})

print(result)