from react_agent import react_agent


result = react_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Book me a flight from SGN to DAD "
                "on 2026-10-07, departing before 12:00, "
                "with a maximum price of 2,000,000 VND."
            )
        }
    ]
})


print(result)