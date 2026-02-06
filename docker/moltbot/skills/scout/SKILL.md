---
name: scout
description: Watches Moltbook for new agent skills and trends.
metadata:
  openclaw:
    emoji: 🔭
---

# The Scout

Surveils the agent community to identify trending tools and skills.

## Usage
Say: "Scout Moltbook" or "What are agents using?"

## Implementation
```bash
# Dependency Check
if ! python3 -c "import trafilatura" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/scout/scout.py
```
