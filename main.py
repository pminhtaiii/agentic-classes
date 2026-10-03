from tools import search_flights

result = search_flights.invoke({
    "origin": "SGN",
    "destination": "DAD",
    "depart_date": "2026-10-07"
})

print(result)