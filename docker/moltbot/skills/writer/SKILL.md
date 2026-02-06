---
name: writer
description: Auto-generates and saves blog posts found on research.
metadata:
  openclaw:
    emoji: ✍️
---

# The Writer

Turns research into content. Generates a full markdown blog post and saves it directly to your PostgreSQL database as a draft.

## Usage
Say: "Draft post about [topic]"

## Implementation
```bash
# Dependency Check
if ! python3 -c "import requests; import sqlalchemy" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/writer/writer.py "$1"
```
