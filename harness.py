from model import Booking, BookingRequest

class VerificationChecker:
    def __init__(self, request: BookingRequest):
        self.request = request
        
    def is_complete(self, booking: Booking) -> dict:
        return (
            booking.status == "confirmed"
            and booking.paid is True
            and booking.origin == self.request.origin
            and booking.destination == self.request.destination
            and booking.depart_date == self.request.depart_date
            and booking.depart_time <= self.request.latest_departure_time
            and booking.price <= self.request.max_price
            and (
                not self.request.require_refundable
                or booking.refundable is True
            )
        )