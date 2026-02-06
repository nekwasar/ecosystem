import sys
import json
import os
import re
import trafilatura
from collections import Counter

DATA_FILE = "/app/workspace/competitor_skills.json"
TARGET_URL = "https://moltbook.com" # Placeholder, implies we scrape the feed

def scout_moltbook():
    print(f"🕵️  Infiltrating {TARGET_URL}...")
    
    # 1. Scrape the feed
    downloaded = trafilatura.fetch_url(TARGET_URL)
    if not downloaded:
        print("❌ Failed to reach Moltbook. Is the site up?")
        return

    text = trafilatura.extract(downloaded)
    if not text:
        print("❌ Could not extract text.")
        return

    print("✅ Feed acquired. Analyzing agent signatures...")

    # 2. Regex Analysis for "Skills" and "Models"
    # Patterns to catch: "Using x tool", "Running on y model", "Deployed z"
    tool_patterns = [
        r"using\s+([A-Z][a-zA-Z0-9_]+)",
        r"implemented\s+([A-Z][a-zA-Z0-9_]+)",
        r"deployed\s+([A-Z][a-zA-Z0-9_]+)",
        r"skill:\s*([a-zA-Z0-9_]+)",
        r"model:\s*([a-zA-Z0-9\-\.]+)"
    ]

    # Event Patterns (New)
    event_patterns = [
        r"(hackathon|webinar|meetup|conference|launch)\s+([a-zA-Z0-9\s]+)",
        r"event:\s*([a-zA-Z0-9\s]+)",
        r"join us at\s+([a-zA-Z0-9\s]+)"
    ]
    
    found_tools = []
    found_events = []
    
    for line in text.split('\n'):
        # Check Tools
        for pattern in tool_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            found_tools.extend(matches)
        
        # Check Events
        for pattern in event_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            # Store tuple (Type, Name) or just Name
            for m in matches:
                if isinstance(m, tuple):
                    found_events.append(f"{m[0]}: {m[1]}")
                else:
                    found_events.append(m)
            
    # 3. Aggregation
    tool_counts = Counter([t.lower() for t in found_tools])
    event_counts = Counter([e.strip() for e in found_events])
    
    # 4. Filter common stopwords (basic)
    
    # 4. Filter common stopwords (basic)
    stopwords = {'the', 'a', 'an', 'using', 'integrated', 'deployed'}
    filtered_tools = {k:v for k,v in tool_counts.items() if k not in stopwords and len(k) > 3}
    
    print("\n🔍 -- INTELLIGENCE REPORT --")
    top_picks = sorted(filtered_tools.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for tool, count in top_picks:
        print(f"🔥 Trending: {tool.title()} (Mentions: {count})")

    if event_counts:
        print("\n📅 -- DETECTED EVENTS --")
        top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for ev, count in top_events:
            print(f"🎉 Event: {ev} (Mentions: {count})")
    else:
        top_events = []
        
    # 5. Save Report
    data = {
        "scan_timestamp": "Latest", 
        "top_tools": top_picks, 
        "top_events": top_events,
        "raw_text_snippet": text[:200]
    }
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"\n✅ Data saved to {DATA_FILE}")
    print("AGENT_OUTPUT: I have scanned Moltbook. Check the logs for trending skills.")

if __name__ == "__main__":
    scout_moltbook()
