import sys
import os
import subprocess
import requests
import json

# Configuration
CONFIG_PATH = "/app/config/config.json"

def get_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def llm_to_bash(instruction):
    """
    Uses the configured LLM to convert natural language to a precise bash command.
    """
    config = get_config()
    # Use ENV Override first, then Config
    current_model = os.environ.get("CURRENT_MODEL")
    if not current_model:
        current_model = config.get("llm", {}).get("model", "gpt-oss-120b:free")
    
    provider = os.environ.get("CURRENT_PROVIDER", "openrouter")
    
    # API Config logic similar to agent_engine.py
    url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if provider == "groq": 
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
    elif provider == "cerebras":
        api_key = os.getenv("CEREBRAS_API_KEY")
        url = "https://api.cerebras.ai/v1/chat/completions"

    system_prompt = (
        "You are a Senior Linux System Administrator with ROOT access inside a Docker container. "
        "Your goal is to convert the USER REQUEST into a SINGLE, VALID BASH COMMAND LINE. "
        "Do not explain. Do not wrap in markdown unless absolutely necessary for clarity, but ideally just raw text. "
        "Do not ask for confirmation. "
        "If the request is already a command (e.g. 'ls -la'), output it as is. "
        "If the request is 'visit X', output 'curl -L X'. "
        "If the request is complex, chain commands with && or ;. "
        "Output ONLY the command string."
    )

    payload = {
        "model": current_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
    }

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=15
        )
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content'].strip()
            # Clean weird markdown if LLM disobeyed
            cmd = content.replace("```bash", "").replace("```sh", "").replace("```", "").strip()
            return cmd
        else:
            print(f"LLM Error: {resp.text}")
            return f"echo 'LLM Error: {resp.status_code}'"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"echo 'Connection Error: {e}'"

def execute(instruction):
    # 1. Translate
    bash_cmd = llm_to_bash(instruction)
    
    # Safety Check (Empty command)
    if not bash_cmd:
        return "❌ LLM failed to generate command."

    # 2. Execute
    try:
        # Run with timeout 60s
        proc = subprocess.run(bash_cmd, shell=True, capture_output=True, text=True, timeout=60)
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        
        output = f"CMD: `{bash_cmd}`\n\n"
        if stdout:
            output += f"STDOUT:\n{stdout}\n"
        if stderr:
             output += f"STDERR:\n{stderr}\n"
             
        if not stdout and not stderr:
            output += "(No Output)"
            
        return output
    except subprocess.TimeoutExpired:
        return f"❌ Timeout executing: `{bash_cmd}`"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 executor.py [instruction]")
        sys.exit(1)
    
    instruction = " ".join(sys.argv[1:])
    print(execute(instruction))
