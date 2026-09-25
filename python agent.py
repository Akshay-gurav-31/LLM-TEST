# agent.py

from openai import OpenAI
import json

client = OpenAI()


# -----------------------------
# Flight Database
# -----------------------------

FLIGHTS = [
    {
        "flight_no": "AI101",
        "airline": "Air India",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "time": "08:00",
        "price": 5500
    },
    {
        "flight_no": "6E202",
        "airline": "IndiGo",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "time": "11:30",
        "price": 4800
    },
    {
        "flight_no": "UK303",
        "airline": "Vistara",
        "from": "Mumbai",
        "to": "Delhi",
        "date": "2026-09-26",
        "time": "18:00",
        "price": 6200
    }
]


# -----------------------------
# Tool 1: Search Flights
# -----------------------------

def search_flights(from_city, to_city, date):

    results = []

    for flight in FLIGHTS:
        if (
            flight["from"].lower() == from_city.lower()
            and flight["to"].lower() == to_city.lower()
            and flight["date"] == date
        ):
            results.append(flight)

    return results


# -----------------------------
# Tool 2: Book Flight
# -----------------------------

def book_flight(flight_no, passenger_name):

    for flight in FLIGHTS:

        if flight["flight_no"] == flight_no:

            booking = {
                "status": "confirmed",
                "booking_id": "BK-" + flight_no + "-92831",
                "passenger": passenger_name,
                "flight": flight
            }

            return booking

    return {
        "status": "failed",
        "message": "Flight not found"
    }


# -----------------------------
# OpenAI Tools
# -----------------------------

tools = [
    {
        "type": "function",
        "name": "search_flights",
        "description": "Search available flights between two cities on a specific date.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_city": {
                    "type": "string"
                },
                "to_city": {
                    "type": "string"
                },
                "date": {
                    "type": "string",
                    "description": "Flight date in YYYY-MM-DD format"
                }
            },
            "required": [
                "from_city",
                "to_city",
                "date"
            ]
        }
    },
    {
        "type": "function",
        "name": "book_flight",
        "description": "Book a flight after the user confirms the selected flight.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_no": {
                    "type": "string"
                },
                "passenger_name": {
                    "type": "string"
                }
            },
            "required": [
                "flight_no",
                "passenger_name"
            ]
        }
    }
]


# -----------------------------
# Agent
# -----------------------------

def run_agent(user_message):

    response = client.responses.create(
        model="gpt-5.6",
        instructions="""
You are a flight booking agent.

Rules:

1. Understand the user's flight request.
2. Use search_flights to find flights.
3. Show available flights clearly.
4. NEVER book a flight without explicit confirmation.
5. Before booking, ask the user:
   "Would you like me to book this flight?"
6. Only call book_flight after the user explicitly says yes.
""",
        input=user_message,
        tools=tools
    )

    return response


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    print("✈️ Flight Booking Agent")
    print("----------------------")

    user_message = input("You: ")

    response = run_agent(user_message)

    print("\nAgent:")

    for item in response.output:

        if item.type == "message":
            for content in item.content:
                if hasattr(content, "text"):
                    print(content.text)

        elif item.type == "function_call":

            args = json.loads(item.arguments)

            if item.name == "search_flights":

                result = search_flights(
                    args["from_city"],
                    args["to_city"],
                    args["date"]
                )

                print(json.dumps(result, indent=2))

            elif item.name == "book_flight":

                result = book_flight(
                    args["flight_no"],
                    args["passenger_name"]
                )

                print(json.dumps(result, indent=2))
