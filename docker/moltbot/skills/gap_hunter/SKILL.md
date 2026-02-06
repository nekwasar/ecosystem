---
name: gap_hunter
description: Analyzes Google Trends vs Search Results to find content gaps.
metadata:
  openclaw:
    emoji: 💰
---

# Gap Hunter

Finds profitable blog topics by calculating the Supply/Demand gap.

## Usage
Say: "Find gaps for [topic]"

## Implementation
```bash
# Dependency Check
if ! python3 -c "import dateutil" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/gap_hunter/hunter.py "$1"
```
