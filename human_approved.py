APPROVED_BOOKINGS: set[str] = set()

def approve_booking(booking_code: str):
    APPROVED_BOOKINGS.add(booking_code)
    
def is_booking_approved(booking_code: str) -> bool:
    return booking_code in APPROVED_BOOKINGS

def reset_approvals():
    APPROVED_BOOKINGS.clear()