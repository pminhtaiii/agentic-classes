from model import BookingRequest, Booking
from harness import VerificationChecker


request = BookingRequest(
    origin="SGN",
    destination="DAD",
    depart_date="2026-10-07",
    latest_departure_time="12:00",
    max_price=2_000_000,
    require_refundable=True
)


booking = Booking(
    booking_code="ABC123",
    flight_id="VN122",
    seat="12A",
    status="confirmed",
    paid=True,
    price=2_300_000,
    origin="SGN",
    destination="DAD",
    depart_date="2026-10-07",
    depart_time="08:10",
    refundable=True
)


checker = VerificationChecker(request)

print(checker.is_complete(booking))