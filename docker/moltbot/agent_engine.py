import os
import json
import logging
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from duckduckgo_search import DDGS

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Paths
WORKSPACE = "/app/workspace"
CONFIG_PATH = "/app/config/config.json"
SOUL_PATH = "/app/config/SOUL.md"

# Load Config
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

config = load_config()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Helper: Read Soul
def get_soul():
    try:
        with open(SOUL_PATH, 'r') as f:
            return f.read()
    except:
        return "You are ROBI, a God-Tier AI agent."

# Helper: Run Skill
def run_skill(script_path, args=[]):
    try:
        cmd = ["python3", script_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Skill Failure: {e}"

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ROBI IS ONLINE. 🚀\nI am ready to dominate.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**COMMANDS:**\n"
        "/roast [target] - Destroy someone.\n"
        "/research [topic] - Get facts.\n"
        "/gap [topic] - Find money.\n"
        "/status - Check my health."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    # 0. Intercept Model Check
    if "which model" in user_text.lower() or user_text.lower() == "/model":
        # Check dynamic env first
        current_model = os.environ.get("CURRENT_MODEL")
        
        # Fallback to config if not switched yet
        if not current_model:
             llm_cfg = config.get("llm", {}).get("providers", {}).get("openrouter", {})
             current_model = llm_cfg.get("model", "gpt-oss-120b:free")

        await update.message.reply_text(f"🧠 **Current Neural Network:** `{current_model}`")
        return

    # 1. Check for specific trigger words if not a command
    if user_text.lower().startswith("roast "):
        target = user_text[6:]
        await update.message.reply_text(f"🔥 Heating up variables for '{target}'...")
        # Run Roaster
        roast_script = f"{WORKSPACE}/docker/moltbot/skills/roaster/roaster.py"
        output = run_skill(roast_script, [target])
        # Parse output to find "Content:" logic or just send raw
        await update.message.reply_text(output[-400:] if len(output) > 2000 else output)
        return

    # 2. Intercept Switching Commands
    lower_text = user_text.lower()
    if lower_text.startswith("switch to"):
        target = lower_text.replace("switch to", "").strip()
        new_model = ""
        new_provider = ""
        
        if "groq" in target:
            new_provider = "groq"
            new_model = "llama-3.3-70b-versatile"
        elif "cerebras" in target:
            new_provider = "cerebras"
            new_model = "llama3.1-70b"
        elif "gpt" in target or "openrouter" in target:
            new_provider = "openrouter"
            new_model = "gpt-oss-120b:free"
        
        if new_provider:
            # Update Runtime Config (In-Memory)
            # Note: For persistence, we'd write to config.json, but for now we set ENV vars for the session
            os.environ["CURRENT_PROVIDER"] = new_provider
            os.environ["CURRENT_MODEL"] = new_model
            await update.message.reply_text(f"🔄 **Switched to {new_provider.upper()}**\nBrain: `{new_model}`")
            return
        else:
            await update.message.reply_text("❌ Unknown provider. Options: Groq, Cerebras, OpenRouter (GPT).")
            return

    # 3. Default: Chat with LLM (The Soul)
    import requests
    
    soul = get_soul()
    
    # Determine Provider & Model
    current_provider = os.environ.get("CURRENT_PROVIDER", "openrouter")
    current_model = os.environ.get("CURRENT_MODEL", config.get("llm", {}).get("model", "gpt-oss-120b:free"))
    
    # API Configs
    providers = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "key": os.getenv("OPENROUTER_API_KEY")
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": os.getenv("GROQ_API_KEY")
        },
        "cerebras": {
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "key": os.getenv("CEREBRAS_API_KEY")
        }
    }
    
    active_cfg = providers.get(current_provider, providers["openrouter"])
    
    payload = {
        "model": current_model,
        "messages": [
            {"role": "system", "content": soul},
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        resp = requests.post(
            active_cfg["url"],
            headers={"Authorization": f"Bearer {active_cfg['key']}"},
            json=payload
        )
        if resp.status_code == 200:
            ai_text = resp.json()['choices'][0]['message']['content']
            await update.message.reply_text(ai_text)
        else:
            await update.message.reply_text(f"Brain Error ({current_provider}): {resp.text}")
    except Exception as e:
        await update.message.reply_text(f"Connection Error: {e}")

# --- MAIN ---
if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("❌ FATAL: TELEGRAM_BOT_TOKEN is missing in env.")
        exit(1)
        
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("✅ ROBI Engine Started. Listening for Telegram events...")
    app.run_polling()
