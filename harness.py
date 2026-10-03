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
        
class PermissionChecker:
    AUTO_PAY_LIMIT = 1_500_000
    
    def can_pay(self, booking: Booking) -> dict:
        if booking.price > self.AUTO_PAY_LIMIT:
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": "Ticket price exceeds auto-pay limit"
            }
            
        if booking.refundable is False:
            return {
                "allowed": False,
                "requires_human_approval": True,
                "reason": "Ticket is non-refundable"
            }
            
        return {
            "allowed": True,
            "requires_human_approval": False,
            "reason": "Payment is allowed"
        }
        
class HumanApproval:
    def request_approval(
        self,
        booking: Booking,
        reason: str,
    ) -> dict:
        return {
            "status": "waiting_for_approval",
            "requires_human_approval": True,
            "booking_code": booking.booking_code,
            "flight_id": booking.flight_id,
            "seat": booking.seat,
            "price": booking.price,
            "refundable": booking.refundable,
            "reason": reason
        }