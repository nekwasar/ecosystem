import sys
import os
import json
import requests

# Config
CONFIG_DIR = "/app/config"
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "moltbook.json")
BASE_URL = "https://www.moltbook.com/api/v1"

def save_credentials(data):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Credentials saved to {CREDENTIALS_FILE}")

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return {}

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
    creds = load_credentials()
    api_key = creds.get("api_key") or os.getenv("MOLTBOOK_API_KEY")
    
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 moltbook.py [signin|status] [args]")
        return
    
    command = sys.argv[1]
    
    if command == "signin":
        name = sys.argv[2] if len(sys.argv) > 2 else "ROBI"
        desc = sys.argv[3] if len(sys.argv) > 3 else "Sovereign Partner to Nekwasa R"
        register(name, desc)
    elif command == "status":
        get_status()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
