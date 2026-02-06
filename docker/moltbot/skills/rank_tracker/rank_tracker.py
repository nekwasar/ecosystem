import sys
import json
import os
import time
from urllib.parse import urlparse
from googlesearch import search as gsearch
from duckduckgo_search import DDGS

# Config
REPORT_DIR = "/app/workspace/seo_reports"
os.makedirs(REPORT_DIR, exist_ok=True)
DEFAULT_TARGET = "nekwasar.com"

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return url

def check_rankings(keyword, target_domain=DEFAULT_TARGET):
    print(f"🕵️  Tracking Rank for '{keyword}' (Target: {target_domain})...")
    
    report = f"# SEO Rank Report: {keyword}\n"
    report += f"**Target Domain:** {target_domain}\n"
    report += f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    engines = ["Google", "DuckDuckGo"]
    grand_competitors = []
    
    for engine in engines:
        print(f"   Scanning {engine}...")
        results = []
        try:
            if engine == "Google":
                # sleep to be polite
                time.sleep(2)
                g_gen = gsearch(keyword, num_results=30, advanced=True)
                results = [{'title': r.title, 'url': r.url} for r in g_gen]
            else:
                with DDGS() as ddgs:
                    d_gen = ddgs.text(keyword, max_results=30)
                    results = [{'title': r['title'], 'url': r['href']} for r in d_gen]
                    
            # Analyze
            found_rank = None
            competitors = []
            
            report += f"## {engine} Results\n"
            
            for i, res in enumerate(results):
                rank = i + 1
                domain = extract_domain(res['url'])
                
                # Check for match
                if target_domain in domain:
                    found_rank = rank
                    title = res['title']
                    report += f"### ✅ YOUR RANK: #{rank}\n"
                    report += f"- **Link**: [{title}]({res['url']})\n\n"
                
                # Collect Competitors (only those above us, or top 5 if we aren't found)
                if found_rank is None or rank < found_rank:
                     if rank <= 5: # Only list top 5 as main competitors to verify
                        competitors.append(f"#{rank} [{domain}]({res['url']})")
                        grand_competitors.append(domain)
            
            if not found_rank:
                report += f"❌ **Not found in Top {len(results)}**\n\n"
            
            report += "**Top Competitors (The people beating you):**\n"
            for c in competitors:
                report += f"- {c}\n"
            report += "\n"
            
        except Exception as e:
            print(f"   ⚠️ Error scanning {engine}: {e}")
            report += f"> Error scanning {engine}: {e}\n\n"

    # Competitor Summary
    report += "## 🏆 Niche Dominators\n"
    report += "Sites that appeared in the Top 5 across engines:\n"
    unique_comps = set(grand_competitors)
    for c in unique_comps:
        # Simple frequency check could go here if we had more data
        report += f"- {c}\n"

    # Save
    filename = f"{keyword.replace(' ', '_')}_rank_report.md"
    file_path = os.path.join(REPORT_DIR, filename)
    with open(file_path, "w") as f:
        f.write(report)
        
    print(f"\n✅ SEO Audit Complete. Report saved to: {file_path}")
    print("AGENT_OUTPUT: Rank check complete. See seo_reports folder.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rank_tracker.py [keyword] [optional_domain]")
        sys.exit(1)
        
    keyword = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TARGET
    
    check_rankings(keyword, domain)
