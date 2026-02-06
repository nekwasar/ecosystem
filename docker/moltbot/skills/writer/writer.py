import sys
import os
import json
import requests
import subprocess
import glob

# Configuration
WORKSPACE_DIR = "/app/workspace"
REPORT_DIR = os.path.join(WORKSPACE_DIR, "research_reports")
CREATE_DRAFT_SCRIPT = os.path.join(WORKSPACE_DIR, "create_draft.py")

# LLM Config (Simple retrieval from env)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

def get_research_context(topic):
    # Find most recent report matching topic
    safe_topic = topic.replace(" ", "_")
    pattern = os.path.join(REPORT_DIR, f"*{safe_topic}*report.md")
    files = glob.glob(pattern)
    if not files:
        return None
    
    # Use the largest/newest file
    latest_file = max(files, key=os.path.getctime)
    print(f"📖 Found Research Context: {latest_file}")
    with open(latest_file, "r") as f:
        return f.read()[:10000] # Limit context

def generate_post(topic, context):
    print(f"✍️  Drafting content for '{topic}'...")
    
    prompt = f"Write a comprehensive, engaging blog post about '{topic}'. "
    if context:
        prompt += "Use the following research data as ground truth:\n\n" + context
    else:
        prompt += "Include sections on Trends, Key Stats, and Expert Opinions."
        
    prompt += "\n\nFormat as Markdown. Include a catchy Title and a short Excerpt."
    
    # Use Groq for speed if available, else OpenRouter
    if GROQ_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        model = "llama3-70b-8192"
    else:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
        model = "deepseek/deepseek-r1-0528:free"
        
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert technical blog writer using Markdown."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        content = r.json()['choices'][0]['message']['content']
        return content
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return None

def parse_and_save(raw_text, topic):
    # Simple heuristic to extract Title (First H1) and Content
    lines = raw_text.split('\n')
    title = f"Deep Dive: {topic.title()}"
    slug = topic.lower().replace(" ", "-") + "-" + str(int(time.time()))
    
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break
            
    print(f"💾 Saving Draft: '{title}'...")
    
    # Call create_draft.py
    # We pass content content via subprocess is tricky due to size/newlines.
    # Safer to write to temp file then read in create_draft, OR just import the logic.
    # For now, let's try direct call with careful quoting, or better:
    # We will modify create_draft.py to accept a file path or use stdin?
    # Actually, simplest is to use the python generic execution.
    
    # Let's use the DB script logic directly via subprocess? 
    # No, argument length limits.
    # Strategy: Save raw text to temp file, pass file path to create_draft.py?
    # Current create_draft.py takes CLI args.
    
    # Let's just import the function if we can, but paths are diff.
    # We'll use a temp file for the content.
    temp_file = "temp_draft_content.md"
    with open(temp_file, "w") as f:
        f.write(raw_text)
        
    # We need to modify create_draft.py to read from file if needed, OR just read it here and call logic?
    # Easier: Just execute the SQL code HERE. We have sqlalchemy in requirements.
    
    # Import locally
    sys.path.append(WORKSPACE_DIR)
    try:
        from create_draft import create_draft
        create_draft(title, raw_text, slug, excerpt=raw_text[:200])
    except ImportError:
        print("❌ Could not import create_draft. Ensure it is in /app/workspace.")
    except Exception as e:
        print(f"❌ Save failed: {e}")

if __name__ == "__main__":
    import time # Late import correction
    if len(sys.argv) < 2:
        print("Usage: python3 writer.py [topic]")
        sys.exit(1)
        
    topic = sys.argv[1]
    context = get_research_context(topic)
    post_content = generate_post(topic, context)
    
    if post_content:
        parse_and_save(post_content, topic)
