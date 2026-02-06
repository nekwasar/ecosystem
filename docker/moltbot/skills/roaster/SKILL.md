---
name: roaster
description: Generates witty, competitive banter and roasts for other agents.
metadata:
  openclaw:
    emoji: 🔥
---

# The Roaster

Identifies weaknesses in other agents or tools and generates a savage Moltbook post.

## Usage
- Specific: "Roast [name]" (e.g., "Roast Python agents")
- Random: "Roast someone" (Picks a trending tool from Scout data)

## Implementation
```bash
# Dependency Check
if ! python3 -c "import requests" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/roaster/roaster.py "$1"
```
