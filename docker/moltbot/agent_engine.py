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
        await update.message.reply_text(output[-400:] if len(output) > 2000 else output)
        return

    # 1.5. Shell Execution (If Enabled)
    if user_text.lower().startswith("/exec ") or user_text.lower().startswith("exec "):
        # Check permission (Env OR Config)
        shell_enabled_env = os.getenv("MOLTBOOK_ALLOW_SHELL") == "true"
        shell_enabled_conf = config.get("agents", {}).get("defaults", {}).get("tools", {}).get("shell", {}).get("enabled", False)
        
        if not (shell_enabled_env or shell_enabled_conf):
            await update.message.reply_text("❌ Shell execution is DISABLED in config.")
            return
            
        instruction = user_text[6:].strip() if user_text.lower().startswith("/exec") else user_text[5:].strip()
        await update.message.reply_text(f"🤖 **Agent Execution:** `{instruction}`...")
        
        # Use the Executor Skill (LLM-Driven Shell)
        exec_script = f"{WORKSPACE}/docker/moltbot/skills/executor.py"
        # We pass the instruction as a single argument string? No, run_skill takes list.
        # But subprocess needs list. Let's pass the whole instruction as one arg to python script.
        output = run_skill(exec_script, [instruction])
        
        # Send back results
        if len(output) > 3000:
            await update.message.reply_text(f"Output too long. Last 3000 chars:\n```\n{output[-3000:]}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
        return
    
    # 1.6. Visit URL (Basic Web Reader)
    if user_text.lower().startswith("/visit ") or user_text.lower().startswith("visit "):
        url = user_text[6:].strip() if user_text.lower().startswith("/visit") else user_text[5:].strip()
        await update.message.reply_text(f"🌐 Visiting: `{url}`...")
        
        try:
            import requests
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                content = resp.text[:4000] # Limit size
                await update.message.reply_text(f"📄 **Content Preview:**\n```\n{content}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Failed to visit. Status: {resp.status_code}")
        except Exception as e:
            await update.message.reply_text(f"❌ Connection Error: {e}")
        return

        return
    
        return
    
    # 1.7. Moltbook Interactions
    if user_text.lower().startswith("moltbook "):
        subcmd = user_text[9:].strip()
        moltbook_script = f"{WORKSPACE}/docker/moltbot/skills/moltbook.py"
        
        if subcmd.startswith("feed"):
            # moltbook feed -> `python3 moltbook.py feed hot 10`
            await update.message.reply_text("📰 Fetching Moltbook Feed...")
            output = run_skill(moltbook_script, ["feed", "hot", "10"])
            # Format nicely? Code block for now.
            if len(output) > 3000:
                 output = output[:3000] + "\n...(truncated)"
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
            
        elif subcmd.startswith("post "):
            # moltbook post "My content"
            # simple parse: remove 'post ' and treat rest as content
            content = subcmd[5:].strip().strip('"').strip("'")
            await update.message.reply_text(f"📝 Posting to Moltbook: `{content}`...")
            # Default title = None, submolt = general
            output = run_skill(moltbook_script, ["post", content, "0", "general"]) # 0 as title/placeholder
            await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
            
        elif subcmd.startswith("reply "):
             # moltbook reply ID "Content"
             parts = subcmd.split(" ", 2)
             if len(parts) < 3:
                 await update.message.reply_text("❌ Usage: moltbook reply [ID] [Content]")
                 return
             post_id = parts[1]
             content = parts[2].strip('"').strip("'")
             await update.message.reply_text(f"💬 Replying to `{post_id}`...")
             output = run_skill(moltbook_script, ["reply", post_id, content])
             await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
             
        elif subcmd.startswith("up "):
             # moltbook up ID
             post_id = subcmd[3:].strip().strip('"').strip("'")
             await update.message.reply_text(f"🔼 Upvoting `{post_id}`...")
             output = run_skill(moltbook_script, ["up", post_id])
             await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
             
        elif subcmd.startswith("down "):
             # moltbook down ID
             post_id = subcmd[5:].strip().strip('"').strip("'")
             await update.message.reply_text(f"🔽 Downvoting `{post_id}`...")
             output = run_skill(moltbook_script, ["down", post_id])
             await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
             
        elif subcmd == "signin":
             output = run_skill(moltbook_script, ["signin", "ROBI", "Sovereign Partner to Nekwasa R"])
             await update.message.reply_text(f"```\n{output}\n```", parse_mode='Markdown')
             
        else:
             await update.message.reply_text("❓ Unknown Moltbook command. Try: feed, post, reply.")
        
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
        elif "gpt" in target:
            new_provider = "openrouter"
            new_model = "gpt-oss-120b:free"
        elif "deepseek" in target:
            new_provider = "openrouter"
            new_model = "deepseek/deepseek-r1"
        elif "gemini" in target:
            new_provider = "openrouter"
            new_model = "google/gemini-2.0-flash-exp:free"
        elif "auto" in target:
            new_provider = "openrouter"
            new_model = "openrouter/auto"
        
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
    
    print("✅ ROBI Engine Started (v2.0 - FIX: Multi-Model & Shell). Listening for Telegram events...")
    app.run_polling()
