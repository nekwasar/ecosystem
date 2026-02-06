import sys
import json
import os

CONFIG_PATH = "/app/config/config.json"

def switch_model(provider_alias):
    # Load Config
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)

    # Define Mappings
    mappings = {
        "deepseek": {"provider": "openrouter", "model": "deepseek/deepseek-r1-0528:free"},
        "gpt": {"provider": "openrouter", "model": "gpt-oss-120b:free"},
        "groq": {"provider": "groq", "model": "llama3-70b-8192"},
        "cerebras": {"provider": "cerebras", "model": "llama3.1-70b"},
        "auto": {"provider": "openrouter", "model": "openrouter/auto"}
    }

    target = mappings.get(provider_alias.lower())
    if not target:
        print(f"Unknown provider alias: {provider_alias}. Use: DeepSeek, GPT, Groq, Cerebras, or Auto.")
        sys.exit(1)

    # Update Config
    config["llm"]["provider"] = target["provider"]
    config["llm"]["model"] = target["model"]

    # Save Config
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"SUCCESS: Switched to {target['provider']} / {target['model']}. Restarting agent to apply...")
    # Trigger restart (OpenClaw watches config.json usually, but we exit 0 to confirm)
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 switcher.py [alias]")
        sys.exit(1)
    
    switch_model(sys.argv[1])
