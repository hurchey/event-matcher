import json
import requests

regions = {
    "Northeast": ["New York", "Boston", "Philadelphia"],
    "West Coast": ["Los Angeles", "San Francisco", "Seattle"],
    "Midwest": ["Chicago", "Detroit", "Minneapolis"],
    "South": ["Houston", "Atlanta", "Miami"],
    "Mountain West": ["Denver", "Salt Lake City", "Phoenix"]
}
API_KEY = "PZRJMHGDWMGPTEUAL5PE"
BASE_URL = "https://www.eventbriteapi.com/v3/events"

# Function to fetch details for a specific event
def get_event_details(event_id):
    url = f"{BASE_URL}/{event_id}/?expand=ticket_availability,venue,category,organizer"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.json().get('error_description', 'Unknown error')}")
        return None

# Function to populate event data from API and save input JSON file
def create_input_json_file(event_ids, output_file):
    print("\nDefine Your Event Strategy:")
    strategy = {
        "target_audience": input("Enter the target audience (e.g., 'Tech professionals, startups'): "),
        "objectives": input("Enter your objectives (e.g., 'Lead generation, networking'): "),
        "industry_sector": input("Enter the desired industry sector (e.g., 'Technology'): "),
        "geographic_focus": input("Enter your geographic focus (e.g., 'Northeast'): "),
        "budget_constraints": input("Enter your budget constraints (e.g., '100-500'): "),
        "kpi": input("Enter your KPIs (e.g., 'Attendees, leads generated'): ")
    }

    events = []
    for event_id in event_ids:
        print(f"Fetching details for event ID: {event_id}...")
        event_data = get_event_details(event_id)
        if event_data:
            venue_data = event_data.get("venue", None)
            address_data = venue_data.get("address", {}) if venue_data else {}
            ticket_availability = event_data.get("ticket_availability", {})
            events.append({
                "event_id": event_id,
                "name": event_data.get("name", {}).get("text", "No name available"),
                "description": event_data.get("description", {}).get("text", "No description available"),
                "start_time": event_data.get("start", {}).get("local", "No start time available"),
                "end_time": event_data.get("end", {}).get("local", "No end time available"),
                "venue": address_data.get("city", "No city available"),
                "category": event_data.get("category", {}).get("name", "No category available"),
                "maximum_ticket_price": ticket_availability.get("maximum_ticket_price", {}).get("display", "N/A"),
                "url": f"https://www.eventbrite.com/e/{event_id}"
            })

    input_data = {
        "strategy": strategy,
        "events": events
    }

    with open(output_file, "w") as file:
        json.dump(input_data, file, indent=4)
    print(f"Input JSON file created: {output_file}")

# Function to get user region based on input location
def get_user_region(user_location):
    for region, cities in regions.items():
        if user_location in cities:
            return region
    return None

# Function to determine if an event matches the user's region
def event_in_user_region(event, user_region):
    for region, cities in regions.items():
        if region == user_region and event["venue"] in cities:
            return True
    return False

# Function to rank and output top 10 events based on region matching
def rank_and_output_events(input_file, output_file, user_location):
    # Load input JSON data
    with open(input_file, "r") as file:
        data = json.load(file)

    strategy = data["strategy"]
    events = data["events"]

    # Determine user region
    user_region = get_user_region(user_location)
    if not user_region:
        print("User location does not match any predefined regions.")
        return

    print(f"User region identified: {user_region}")

    # Rank events by region match and other criteria
    ranked_events = []
    for event in events:
        relevance_score = 0

        # Region-based relevance
        if event_in_user_region(event, user_region):
            relevance_score += 50  # Assign high weight for region match

        # Match objectives
        if strategy["objectives"].lower() in event["description"].lower():
            relevance_score += 25

        # Match industry sector
        if strategy["industry_sector"].lower() in event["category"].lower():
            relevance_score += 25

        # Add to ranked list
        event["relevance_score"] = relevance_score
        ranked_events.append(event)

    # Sort events by relevance score
    ranked_events.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Extract top 10 events
    top_events = ranked_events[:10]

    # Save and display results
    with open(output_file, "w") as file:
        for idx, event in enumerate(top_events, start=1):
            result = {
                "Event Name": event["name"],
                "Event URL": event["url"],
                "Brief Description": event["description"],
                "Relevance Rank": idx
            }
            file.write(json.dumps(result, indent=4) + "\n\n")
            print(json.dumps(result, indent=4) + "\n")

    print(f"\nTop 10 events saved to {output_file}")

# Main function
def main():
    event_ids = [
        "146584912419", "1074663911689", "938781269047",
        "743897235657", "1002711155057", "984312454047",
        "1069749151509", "1053366199659", "916568159037",
        "778446312877"
    ]
    input_file = "input_events.json"
    output_file = "top_10_events.txt"

    # Step 1: Create input JSON file with API data
    create_input_json_file(event_ids, input_file)

    # Step 2: Rank and output top events
    user_location = input("Enter your location (e.g., 'New York'): ")
    rank_and_output_events(input_file, output_file, user_location)

if __name__ == "__main__":
    main()