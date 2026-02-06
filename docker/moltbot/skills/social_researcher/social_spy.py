import sys
import json
import os
import time
from duckduckgo_search import DDGS
import trafilatura

# Ensure we can save reports
REPORT_DIR = "/app/workspace/social_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def search_platform(topic, platform, query_modifier, max_results=5):
    full_query = f'site:{platform} "{topic}" {query_modifier}'
    print(f"📡 Scanning {platform} for: {query_modifier}...")
    results = []
    try:
        with DDGS() as ddgs:
            # We use 'text' search as it's most robust for targeted operators
            search_res = list(ddgs.text(full_query, max_results=max_results))
            for r in search_res:
                results.append(r)
    except Exception as e:
        print(f"   ⚠️ Error scanning {platform}: {e}")
    return results

def deep_scrape(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            # Basic cleanup: remove very short lines, keep main content
            if text:
                return text[:1000] # Capture first 1000 chars of discussion
    except:
        pass
    return None

def conduct_social_research(topic):
    print(f"🧠 Initiating EXTENSIVE Social Research on: {topic}\n")
    
    report = f"# Social Intelligence Report: {topic}\n\n"
    
    # 1. Pain Points (Reddit) - Essential for finding problems to solve
    print("--- Phase 1: Identifying Pain Points (Reddit) ---")
    pain_queries = ["sucks", "hate", "problem", "broken", "alternative to"]
    report += "## 😡 Pain Points & Complaints\n"
    
    for q in pain_queries:
        results = search_platform(topic, "reddit.com", q, max_results=3)
        for res in results:
            content = deep_scrape(res['href'])
            report += f"### {res['title']}\n"
            report += f"- **Source**: [Reddit]({res['href']})\n"
            if content:
                report += f"> {content[:300]}...\n\n"
            else:
                report += f"> *Could not scrape content*\n\n"

    # 2. Questions & Gaps (Quora/Reddit) - Essential for content ideas
    print("\n--- Phase 2: Identifying Knowledge Gaps (Quora & Reddit) ---")
    question_queries = ["how to", "help with", "guide", "tutorial"]
    report += "## ❓ Unanswered Questions & Gaps\n"
    
    for q in question_queries:
        # Check Quora
        results = search_platform(topic, "quora.com", q, max_results=2)
        for res in results:
            report += f"- **[Quora]** [{res['title']}]({res['href']})\n"
            
        # Check Reddit
        results2 = search_platform(topic, "reddit.com", q, max_results=2)
        for res in results2:
            report += f"- **[Reddit]** [{res['title']}]({res['href']})\n"
    
    report += "\n"

    # 3. Visual/Video Trends (YouTube/TikTok)
    print("\n--- Phase 3: Analyzing Visual Trends (YouTube) ---")
    report += "## 📺 Video & Visual Trends\n"
    yt_results = search_platform(topic, "youtube.com", "review OR guide", max_results=5)
    for res in yt_results:
        report += f"- [{res['title']}]({res['href']})\n"

    # 4. Real-time Buzz (Twitter/X)
    print("\n--- Phase 4: Real-time Sentinel (X/Twitter) ---")
    report += "\n## 🐦 Real-time Buzz (X/Twitter)\n"
    x_results = search_platform(topic, "twitter.com", "latest", max_results=5)
    for res in x_results:
        snippet = deep_scrape(res['href'])
        report += f"- **{res['title']}**\n"
        if snippet:
             report += f"  > {snippet[:150]}...\n"

    # Save
    filename = f"{topic.replace(' ', '_')}_social_report.md"
    file_path = os.path.join(REPORT_DIR, filename)
    with open(file_path, "w") as f:
        f.write(report)
        
    print(f"\n✅ Mission Complete. Social profile built at: {file_path}")
    print("AGENT_OUTPUT: I have finished targeting social channels. Check the social_reports folder.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 social_spy.py [topic]")
        sys.exit(1)
        
    conduct_social_research(sys.argv[1])
