---
name: researcher
description: Conducts deep, recursive research using live web data.
metadata:
  openclaw:
    emoji: 🕵️
  install:
    pip:
      - duckduckgo-search
      - googlesearch-python
      - trafilatura
---

# S-Rank Researcher

Conducts a recursive deep dive into a topic, scraping real-time data from the web.

## Usage
Say: "Research [topic]"

## Implementation
```bash
# Ensure dependencies are installed (first run only check)
if ! python3 -c "import googlesearch" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/researcher/researcher.py "$1"
```
