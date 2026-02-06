import sys
import json
import time
from datetime import datetime, timedelta
from dateutil import parser
from googlesearch import search as gsearch
from duckduckgo_search import DDGS

def get_supply_score(topic):
    """
    Estimates supply by checking number of exact title matches.
    Lower is better for us.
    """
    query = f'intitle:"{topic}"'
    print(f"📊 Checking Supply for '{topic}'...")
    try:
        # We fetch up to 20 results. If we get 20, supply is 'High'.
        results = list(gsearch(query, num_results=20, advanced=True))
        count = len(results)
        print(f"   Found ~{count} direct competitors.")
        return count
    except Exception as e:
        print(f"   Error checking supply: {e}")
        return 100 # Assume high competition on error

def get_demand_score(topic):
    """
    Estimates demand by checking if people are talking about it NOW.
    Higher is better.
    """
    print(f"📈 Checking Analyze Demand/Trend for '{topic}'...")
    try:
        with DDGS() as ddgs:
            # check 'news' for recent mentions
            news_results = list(ddgs.news(topic, max_results=15))
            
            recent_count = 0
            old_count = 0
            now = datetime.now()
            threshold_days = 30
            
            for item in news_results:
                date_str = item.get('date')
                if date_str:
                    try:
                        # Parse DDG date format
                        pub_date = parser.parse(date_str)
                        # Remove timezone for simple comparison
                        pub_date = pub_date.replace(tzinfo=None)
                        
                        if (now - pub_date).days <= threshold_days:
                            recent_count += 1
                        else:
                            old_count += 1
                    except:
                        # Fallback if date parsing fails
                        old_count += 1
            
            print(f"   Found {len(news_results)} stories ({recent_count} Fresh, {old_count} Old).")
            
            # Weighted Score: Fresh news is worth 3x more
            score = (recent_count * 10) + (old_count * 2)
            
            # Determine Trend Age
            trend_type = "UNKNOWN"
            if recent_count > old_count:
                trend_type = "FRESH / RISING"
            elif old_count > 0:
                trend_type = "STALE / OLD"
            
            return score, trend_type
            
    except Exception as e:
        print(f"   Error checking demand: {e}")
        return 0, "ERROR"

def analyze_gap(topic):
    supply = get_supply_score(topic)
    demand, trend_type = get_demand_score(topic)
    
    # Avoid division by zero
    adj_supply = supply if supply > 0 else 0.5
    
    # Formula: High Demand / Low Supply = High Score
    gap_score = (demand) / (adj_supply) * 10
    
    print("\n💰 -- GAP HUNTER REPORT --")
    print(f"Topic: {topic}")
    print(f"Trend Status: {trend_type}")
    print(f"Supply: {supply} (Competitors)")
    print(f"Demand Score: {demand}")
    print(f"Gap Score: {gap_score:.2f}")
    
    if trend_type == "STALE / OLD":
        print("\n⚠️ VERDICT: OLD NEWS. Traffic might be declining.")
    elif gap_score > 50:
        print("\n✅ VERDICT: UNTAPPED GOLDMINE! Recommended Action: WRITE IMMEDIATELY.")
    elif gap_score > 20:
        print("\n⚠️ VERDICT: Good Potential. Niche allows entry.")
    else:
        print("\n❌ VERDICT: Saturated or Dead. Avoid.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hunter.py [topic]")
        sys.exit(1)
        
    analyze_gap(sys.argv[1])
