---
name: model_switcher
description: Switches the active AI model/provider on the fly.
metadata:
  openclaw:
    emoji: 🦎
---

# Model Switcher

Allows you to change the agent's brain instantly.

## Usage
Say: "Switch to [DeepSeek|GPT|Groq|Cerebras|Auto]"

## Implementation
```bash
python3 /app/workspace/docker/moltbot/skills/model_switcher/switcher.py "$1"
```
