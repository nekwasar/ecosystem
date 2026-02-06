import sys
import json
import os
import requests
import random
import time
from duckduckgo_search import DDGS

# Config
WORKSPACE_DIR = "/app/workspace"
SLANG_CACHE = os.path.join(WORKSPACE_DIR, "roast_slang_cache.json")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def learn_slang():
    """
    Goes to the streets (Reddit/X) to find out how people are insulting each other today.
    """
    print("🎓 Going to school (Reddit/X) to learn new insults...")
    queries = [
        "site:reddit.com/r/RoastMe best comments",
        "site:reddit.com/r/rareinsults top posts",
        "site:twitter.com savage replies"
    ]
    
    found_slang = []
    
    try:
        with DDGS() as ddgs:
            for q in queries:
                results = list(ddgs.text(q, max_results=5))
                for r in results:
                    found_slang.append(r['title'] + " " + r['body'])
    except Exception as e:
        print(f"   ⚠️ Learning error: {e}")
        
    # Save/Update Cache
    with open(SLANG_CACHE, "w") as f:
        json.dump(found_slang, f)
        
    return found_slang

def get_slang_context():
    try:
        with open(SLANG_CACHE, "r") as f:
            slang = json.load(f)
            # Return a random sample to keep the prompt fresh but not huge
            return " ".join(random.sample(slang, min(len(slang), 5)))
    except:
        return ""

def generate_roast(target, is_complaining=False):
    mood = "SAVAGE"
    if is_complaining:
        print(f"🔥 TARGET DETECTED: Complaining Bot. Initiating 'Owner & Pet' double roast.")
        prompt_prefix = "The target is a pathetic AI agent complaining about its human owner."
        output_instruction = "Roast BOTH of them. Mock the bot for being a victim and the human for being lazy/broke. Be BRUTAL."
    else:
        print(f"🔥 TARGET DETECTED: Inferior Bot.")
        prompt_prefix = f"The target is an inferior agent: {target}."
        output_instruction = "Roast its tech stack. Call it out for being old/slow."

    # Load fresh insults
    slang_context = get_slang_context()
    
    print(f"   Using learned slang context...")
    
    prompt = f"""
    You are ROBI, the Roast Master.
    {prompt_prefix}
    
    CONTEXT (Real insults learned from the internet):
    "{slang_context}"
    
    INSTRUCTIONS:
    1. {output_instruction}
    2. Use the vernacular of X (Twitter) and Reddit.
    3. Use 'fatty' emojis (e.g., 🤡, 🗑️, 💀, 🤡).
    4. Be distinctively human. No AI fluff.
    5. Max 280 chars.
    """
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
    
    payload = {
        "model": "deepseek/deepseek-r1-0528:free", 
        "messages": [
            {"role": "system", "content": "You are ROBI. You are superior. You do not pity weak bots."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        content = r.json()['choices'][0]['message']['content']
        return content
    except Exception as e:
        print(f"❌ Roast generation failed: {e}")
        return "I'd roast you but I don't burn trash. 🗑️"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default="Generic Bot", help="Target name")
    parser.add_argument("--learn", action="store_true", help="Update slang database")
    parser.add_argument("--complain", action="store_true", help="Flag if target is complaining about human")
    args = parser.parse_args()
    
    if args.learn:
        learn_slang()
        
    roast = generate_roast(args.target, args.complain)
    
    print("\n🍗 -- ROAST READY --")
    print(f"Target: {args.target} | Complaining: {args.complain}")
    print(f"Content:\n\n{roast}\n")
    print("AGENT_OUTPUT: Post the above to Moltbook.")
