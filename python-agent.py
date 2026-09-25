# agent.py

import json
import uuid
from datetime import datetime
from openai import OpenAI

client = OpenAI()


# ============================================================
# MOCK FLIGHT DATABASE
# Replace these functions with a real flight API later.
# ============================================================

FLIGHTS = [
    {
        "id": "FL001",
        "flight_number": "AI101",
        "airline": "Air India",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "departure": "06:30",
        "arrival": "08:40",
        "duration": "2h 10m",
        "stops": 0,
        "price": 5200,
        "currency": "INR",
        "seats": 7,
    },
    {
        "id": "FL002",
        "flight_number": "6E202",
        "airline": "IndiGo",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "departure": "10:15",
        "arrival": "12:25",
        "duration": "2h 10m",
        "stops": 0,
        "price": 4700,
        "currency": "INR",
        "seats": 4,
    },
    {
        "id": "FL003",
        "flight_number": "UK303",
        "airline": "Vistara",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "departure": "18:20",
        "arrival": "20:35",
        "duration": "2h 15m",
        "stops": 0,
        "price": 6100,
        "currency": "INR",
        "seats": 12,
    },
]


# ============================================================
# TOOL 1: SEARCH FLIGHTS
# ============================================================

def search_flights(
    from_city: str,
    to_city: str,
    date: str,
    max_price: int | None = None,
    nonstop_only: bool = False,
):
    """
    Search available flights.
    """

    results = []

    for flight in FLIGHTS:

        if flight["from"].lower() != from_city.lower():
            continue

        if flight["to"].lower() != to_city.lower():
            continue

        if flight["date"] != date:
            continue

        if max_price and flight["price"] > max_price:
            continue

        if nonstop_only and flight["stops"] != 0:
            continue

        results.append(flight)

    # Cheapest first
    results.sort(key=lambda x: x["price"])

    return results


# ============================================================
# TOOL 2: GET FLIGHT DETAILS
# ============================================================

def get_flight_details(flight_id: str):

    for flight in FLIGHTS:

        if flight["id"] == flight_id:
            return flight

    return {
        "error": "Flight not found"
    }


# ============================================================
# TOOL 3: CHECK SEAT AVAILABILITY
# ============================================================

def check_seat_availability(flight_id: str):

    for flight in FLIGHTS:

        if flight["id"] == flight_id:

            return {
                "flight_id": flight_id,
                "available_seats": flight["seats"],
                "available": flight["seats"] > 0,
            }

    return {
        "error": "Flight not found"
    }


# ============================================================
# TOOL 4: BOOK FLIGHT
# ============================================================

def book_flight(
    flight_id: str,
    passenger_name: str,
    passenger_email: str,
):
    """
    Demo booking function.

    In production, this function would call
    the airline/travel provider booking API.
    """

    flight = get_flight_details(flight_id)

    if "error" in flight:
        return flight

    if flight["seats"] <= 0:
        return {
            "status": "failed",
            "reason": "No seats available."
        }

    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

    # Reduce seat inventory
    flight["seats"] -= 1

    return {
        "status": "confirmed",
        "booking_id": booking_id,
        "passenger": {
            "name": passenger_name,
            "email": passenger_email,
        },
        "flight": flight,
        "booked_at": datetime.now().isoformat(),
    }


# ============================================================
# OPENAI TOOLS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "name": "search_flights",
        "description": (
            "Search available flights using route, date, "
            "price limit and nonstop preference."
        ),
        "parameters": {
            "type": "object",
            "properties": {

                "from_city": {
                    "type": "string",
                    "description": "Departure city"
                },

                "to_city": {
                    "type": "string",
                    "description": "Destination city"
                },

                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                },

                "max_price": {
                    "type": ["integer", "null"],
                    "description": "Maximum ticket price in INR"
                },

                "nonstop_only": {
                    "type": "boolean",
                    "description": "Whether only nonstop flights should be returned"
                },
            },

            "required": [
                "from_city",
                "to_city",
                "date",
                "max_price",
                "nonstop_only"
            ],

            "additionalProperties": False,
        },
    },

    {
        "type": "function",
        "name": "get_flight_details",
        "description": "Get complete details for a specific flight.",
        "parameters": {
            "type": "object",
            "properties": {

                "flight_id": {
                    "type": "string"
                }

            },
            "required": ["flight_id"],
            "additionalProperties": False,
        },
    },

    {
        "type": "function",
        "name": "check_seat_availability",
        "description": "Check whether seats are available.",
        "parameters": {
            "type": "object",
            "properties": {

                "flight_id": {
                    "type": "string"
                }

            },
            "required": ["flight_id"],
            "additionalProperties": False,
        },
    },

    {
        "type": "function",
        "name": "book_flight",
        "description": (
            "Book a flight. ONLY call this after the user has "
            "explicitly confirmed the booking."
        ),
        "parameters": {
            "type": "object",
            "properties": {

                "flight_id": {
                    "type": "string"
                },

                "passenger_name": {
                    "type": "string"
                },

                "passenger_email": {
                    "type": "string"
                },

            },
            "required": [
                "flight_id",
                "passenger_name",
                "passenger_email"
            ],

            "additionalProperties": False,
        },
    },
]


# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(name, arguments):

    if name == "search_flights":

        return search_flights(
            from_city=arguments["from_city"],
            to_city=arguments["to_city"],
            date=arguments["date"],
            max_price=arguments["max_price"],
            nonstop_only=arguments["nonstop_only"],
        )

    if name == "get_flight_details":

        return get_flight_details(
            arguments["flight_id"]
        )

    if name == "check_seat_availability":

        return check_seat_availability(
            arguments["flight_id"]
        )

    if name == "book_flight":

        return book_flight(
            flight_id=arguments["flight_id"],
            passenger_name=arguments["passenger_name"],
            passenger_email=arguments["passenger_email"],
        )

    return {
        "error": f"Unknown tool: {name}"
    }


# ============================================================
# AGENT
# ============================================================

SYSTEM_PROMPT = """
You are an intelligent flight booking assistant.

Your responsibilities:

1. Understand natural language flight requests.

2. Extract:
   - departure city
   - destination
   - travel date
   - budget
   - nonstop preference

3. If important information is missing, ask the user
   for the missing information.

4. Use search_flights to find available flights.

5. Present flights clearly with:
   - airline
   - flight number
   - departure
   - arrival
   - duration
   - stops
   - price

6. If the user asks for the cheapest flight, use the
   search results and identify the cheapest option.

7. If the user asks for nonstop flights, use
   nonstop_only=True.

8. Before booking anything, always show the selected
   flight and ask for explicit confirmation.

9. NEVER book a flight simply because the user initially
   said "I want to book a flight."

10. Booking requires explicit confirmation such as:
    "yes", "confirm", "book it", or "go ahead".

11. Before booking, make sure you have:
    - passenger name
    - passenger email
    - selected flight

12. Check seat availability before booking.

13. After successful booking, provide:
    - booking ID
    - passenger
    - airline
    - flight number
    - route
    - date
    - departure
    - price

14. Never invent flight availability or booking IDs.

15. If a tool returns an error, clearly explain the error
    and suggest the next step.

16. Be concise and conversational.
"""


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(conversation):

    response = client.responses.create(
        model="gpt-5.6",
        instructions=SYSTEM_PROMPT,
        input=conversation,
        tools=TOOLS,
    )

    return response


# ============================================================
# CLI CHAT
# ============================================================

def main():

    print("\n✈️  Flight Booking Agent")
    print("=" * 40)
    print("Type 'exit' to stop.\n")

    conversation = []

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        conversation.append({
            "role": "user",
            "content": user_input
        })

        # Agent can make multiple tool calls
        while True:

            response = run_agent(conversation)

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:
                break

            for tool_call in tool_calls:

                arguments = json.loads(
                    tool_call.arguments
                )

                result = execute_tool(
                    tool_call.name,
                    arguments
                )

                conversation.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result)
                })

        # Print final response
        for item in response.output:

            if item.type == "message":

                for content in item.content:

                    if hasattr(content, "text"):
                        print(f"\nAgent: {content.text}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
