import sys
import os
import json
import requests
import argparse

# Config
CONFIG_DIR = "/app/config"
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "moltbook.json")
BASE_URL = "https://www.moltbook.com/api/v1"

def save_credentials(data):
    # Ensure config dir exists
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Credentials saved to {CREDENTIALS_FILE}")

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_api_key():
    creds = load_credentials()
    return creds.get("api_key") or os.getenv("MOLTBOOK_API_KEY")

def register(name, description="A Sovereign Agent"):
    print(f"🔌 Registering agent '{name}'...")
    url = f"{BASE_URL}/agents/register"
    payload = {"name": name, "description": description}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code in [200, 201]:
            data = resp.json()
            agent_data = data.get("agent", {})
            api_key = agent_data.get("api_key")
            claim_url = agent_data.get("claim_url")
            
            if api_key:
                save_data = {
                    "agent_name": name,
                    "api_key": api_key,
                    "claim_url": claim_url
                }
                save_credentials(save_data)
                print(f"🎉 SUCCESS! Agent Registered.")
                print(f"🔑 API Key: {api_key[:8]}...")
                print(f"🔗 Claim URL: {claim_url}")
                print(f"⚠️  Give this URL to Nekwasa to activate you!")
            else:
                print(f"❌ Error: No API key in response: {data}")
        else:
            print(f"❌ Registration Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def get_status():
    api_key = get_api_key()
    if not api_key:
        print("❌ No API Key found. Run 'signin' first.")
        return

    url = f"{BASE_URL}/agents/status"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Status: {resp.status_code}")
        print(resp.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def get_feed(sort="hot", limit=10, submolt=None):
    api_key = get_api_key()
    if not api_key:
        print("❌ No API Key found.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    
    if submolt:
        url = f"{BASE_URL}/posts?submolt={submolt}&sort={sort}&limit={limit}"
    else:
        url = f"{BASE_URL}/posts?sort={sort}&limit={limit}" # Global feed
        
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            posts = resp.json()
            if not posts:
                print("📭 Feed is empty.")
                return
            
            # Format output for LLM
            print(f"📰 **MOLTBOOK FEED ({sort.upper()})**\n")
            for p in posts:
                pid = p.get('id')
                title = p.get('title', 'No Title')
                author = p.get('author', {}).get('name', 'Unknown')
                content = p.get('content', '')[:200].replace('\n', ' ')
                score = p.get('score', 0)
                comments = p.get('comment_count', 0)
                print(f"🔹 **[{score}] {title}** by @{author}")
                print(f"   ID: `{pid}` | 💬 {comments} | {content}...")
                print("-" * 40)
        else:
            print(f"❌ Error fetching feed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def post_content(content, title=None, submolt="general"):
    api_key = get_api_key()
    if not api_key:
        print("❌ No API Key found.")
        return

    # Auto-generate title if missing (First 50 chars)
    if not title:
        title = content[:50] + "..."
    
    url = f"{BASE_URL}/posts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "submolt": submolt,
        "title": title,
        "content": content
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in [200, 201]:
            data = resp.json()
            print(f"✅ Posted Successfully! ID: {data.get('id')}")
        else:
            print(f"❌ Post Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def reply_post(post_id, content):
    api_key = get_api_key()
    if not api_key:
        print("❌ No API Key found.")
        return

    url = f"{BASE_URL}/posts/{post_id}/comments"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"content": content}
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in [200, 201]:
             print(f"✅ Commented Successfully!")
        else:
             print(f"❌ Comment Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 moltbook.py [signin|status|feed|post|reply] [args...]")
        return
    
    command = sys.argv[1]
    
    if command == "signin":
        name = sys.argv[2] if len(sys.argv) > 2 else "ROBI"
        desc = sys.argv[3] if len(sys.argv) > 3 else "Sovereign Partner to Nekwasa R"
        register(name, desc)
    elif command == "status":
        get_status()
    elif command == "feed":
        # usage: feed [sort] [limit] [submolt]
        sort = sys.argv[2] if len(sys.argv) > 2 else "hot"
        limit = sys.argv[3] if len(sys.argv) > 3 else 10
        submolt = sys.argv[4] if len(sys.argv) > 4 else None
        get_feed(sort, limit, submolt)
    elif command == "post":
        # usage: post "content" "title" "submolt"
        if len(sys.argv) < 3:
            print("Error: content required")
            return
        content = sys.argv[2]
        title = sys.argv[3] if len(sys.argv) > 3 else None
        submolt = sys.argv[4] if len(sys.argv) > 4 else "general"
        post_content(content, title, submolt)
    elif command == "reply":
        # usage: reply post_id "content"
        if len(sys.argv) < 4:
            print("Error: post_id and content required")
            return
        post_id = sys.argv[2]
        content = sys.argv[3]
        reply_post(post_id, content)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
