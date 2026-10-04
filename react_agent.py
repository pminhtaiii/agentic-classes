from tools import (
    search_flights,
    check_seat,
    book_seat,
    pay,
    get_booking
)
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from middleware import permission_guard

load_dotenv()

TOOLS = [
    search_flights,
    check_seat,
    book_seat,
    pay,
    get_booking
]

model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite',
    temperature=0
)

SYSTEM_PROMPT = """
You are a flight booking agent.

Use the provided tools to obtain flight and booking information.

Rules:
- Never invent flight IDs.
- Never invent prices.
- Never invent seat numbers.
- Never invent booking codes.
- Search for flights before selecting one.
- Check seat availability before booking.
- Verify booking status before claiming the task is complete.
"""

react_agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    middleware=[permission_guard],
)
