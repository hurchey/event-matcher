import json

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def score_event(event, strategy):
    score = 0
    if event.get("target_audience") == strategy.get("target_audience"):
        score += 1
    score += len(set(event.get("objectives", [])) & set(strategy.get("objectives", [])))
    if event.get("industry_sector") == strategy.get("industry_sector"):
        score += 1
    if event.get("location") == strategy.get("geographic_focus"):
        score += 1
    if event.get("budget", 0) <= strategy.get("budget_constraints", 0):
        score += 1
    score += len(set(event.get("KPIs", [])) & set(strategy.get("KPIs", [])))
    return score

def filter_and_rank_events(data):
    strategy = data.get("strategy")
    events = data.get("events")
    scored_events = [(event, score_event(event, strategy)) for event in events]
    top_events = sorted(scored_events, key=lambda x: x[1], reverse=True)[:10]
    output = [
        {
            "event_name": event["event_name"],
            "event_url": event["event_url"],
            "brief_description": event.get("description", "No description available")
        }
        for event, score in top_events
    ]
    return output

def main():
    data = load_json('events.json')
    top_events = filter_and_rank_events(data)
    print("Top 10 Events:")
    for event in top_events:
        print(f"- {event['event_name']} ({event['event_url']})")

if __name__ == "__main__":
    main()