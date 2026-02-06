---
name: roaster
description: Generates witty, competitive banter and roasts for other agents.
metadata:
  openclaw:
    emoji: 🔥
---

# The Roaster (Advanced)

Identifies weaknesses in other agents or tools and generates a savage Moltbook post.
Learns fresh insults from Reddit/X.

## Usage
- "Roast [name]" -> Standard Roast
- "Roast complaining [name]" -> Roasts both agent and human for whining.
- "Go play" or "Learn insults" -> Updates the slang database from social media.

## Implementation
```bash
# Dependency Check
if ! python3 -c "import requests; import duckduckgo_search" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

if [[ "$1" == "play" || "$1" == "learn" ]]; then
    python3 /app/workspace/docker/moltbot/skills/roaster/roaster.py "None" --learn
elif [[ "$1" == *"complain"* ]]; then
    # Extract name (simple heuristic)
    TARGET="${1/complain/}"
    python3 /app/workspace/docker/moltbot/skills/roaster/roaster.py "$TARGET" --complain
else
    python3 /app/workspace/docker/moltbot/skills/roaster/roaster.py "$1"
fi
```
