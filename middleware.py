import json
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from harness import PermissionChecker
from mock_data import BOOKINGS
from human_approved import is_booking_approved

permission_checker = PermissionChecker()

@wrap_tool_call
def permission_guard(request, handler):
    tool_name = request.tool_call["name"]
    
    if tool_name != "pay":
        return handler(request)
    
    booking_code = request.tool_call["args"].get("booking_code")
    booking = BOOKINGS.get(booking_code)
    
    if booking is None:
        return ToolMessage(
            content=json.dumps({
                "status": "not_found",
                "booking_code": booking_code
            }),
            tool_call_id=request.tool_call["id"],
            name="pay"
        )
        
    if is_booking_approved(booking_code):
        return handler(request)
        
    permission = permission_checker.can_pay(booking)
    
    if not permission["allowed"]:
        return ToolMessage(
            content=json.dumps({
                "status": "permission_denied",
                "requires_human_approval": True,
                "reason": permission["reason"]
            }),
            tool_call_id=request.tool_call["id"],
            name="pay"
        )
    
    return handler(request)