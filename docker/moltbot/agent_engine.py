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
        # Find the model being used
        llm_cfg = config.get("llm", {}).get("providers", {}).get("openrouter", {})
        current_model = llm_cfg.get("model", "deepseek/deepseek-r1-0528:free")
        # Also check env override
        if os.getenv("OPENROUTER_MODEL_PREF"):
            current_model = os.getenv("OPENROUTER_MODEL_PREF")
            
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

    # 2. Default: Chat with LLM (The Soul)
    # We use a simple HTTP request to openrouter here for the "Chat" capability
    # to avoid importing the huge 'openai' lib just for one call, keeping it light.
    import requests
    
    soul = get_soul()
    
    # Provider Config
    llm_cfg = config.get("llm", {}).get("providers", {}).get("openrouter", {})
    api_key = os.getenv("OPENROUTER_API_KEY") 
    model = "gpt-oss-120b:free"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": soul},
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload
        )
        if resp.status_code == 200:
            ai_text = resp.json()['choices'][0]['message']['content']
            await update.message.reply_text(ai_text)
        else:
            await update.message.reply_text(f"Brain Error: {resp.text}")
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
