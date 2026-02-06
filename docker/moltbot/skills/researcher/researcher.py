import sys
import json
import os
from duckduckgo_search import DDGS
from googlesearch import search as gsearch
import trafilatura
import time

# Ensure we can save reports
REPORT_DIR = "/app/workspace/research_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def search_engine_aggregator(query, max_results=5):
    print(f"🔍 Searching for: {query}...")
    combined_results = []
    seen_urls = set()

    # 1. DuckDuckGo Search
    try:
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, max_results=max_results))
            for res in ddg_results:
                if res['href'] not in seen_urls:
                    combined_results.append({'title': res['title'], 'url': res['href'], 'source': 'DuckDuckGo'})
                    seen_urls.add(res['href'])
    except Exception as e:
        print(f"  ⚠️ DuckDuckGo Error: {e}")

    # 2. Google Search (googlesearch-python)
    try:
        # Pause to avoid rate limits
        time.sleep(1) 
        google_results = gsearch(query, num_results=max_results, advanced=True)
        for res in google_results:
            if res.url not in seen_urls:
                combined_results.append({'title': res.title, 'url': res.url, 'source': 'Google'})
                seen_urls.add(res.url)
    except Exception as e:
        print(f"  ⚠️ Google Error: {e}")

    return combined_results

def search_and_scrape(query, max_results=3):
    # Get aggregated results
    search_results = search_engine_aggregator(query, max_results=max_results)
        
    results = []
    for res in search_results:
        url = res['url']
        title = res['title']
        source = res['source']
        print(f"  ⬇️ Scraping ({source}): {title}...")
        
        # 2. Scrape Content
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                results.append({
                    "title": title,
                    "url": url,
                    "content": text[:5000] # Limit context window
                })
    
    return results

def recursive_research(topic):
    print(f"🚀 Starting S-Rank Research on: {topic}")
    
    # Decompose (Extensive S-Rank Strategy)
    sub_queries = [
        f"{topic} latest trends and news 2026",
        f"{topic} market statistics and data analysis",
        f"{topic} expert opinions and thought leadership",
        f"{topic} top competitors and alternatives",
        f"{topic} future outlook and predictions 2027",
        f"{topic} controversies and challenges"
    ]
    
    final_report = f"# Research Report: {topic}\n\n"
    
    for q in sub_queries:
        data = search_and_scrape(q, max_results=2)
        for item in data:
            final_report += f"## Source: {item['title']}\n"
            final_report += f"**URL**: {item['url']}\n\n"
            final_report += f"```text\n{item['content']}\n```\n\n"
            
    # Save Report
    filename = f"{topic.replace(' ', '_')}_report.md"
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w") as f:
        f.write(final_report)
        
    print(f"✅ Research Complete! Report saved to: {path}")
    print("AGENT_OUTPUT: I have compiled a detailed report. You can ask me to summarize it now.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 researcher.py [topic]")
        sys.exit(1)
        
    recursive_research(sys.argv[1])
