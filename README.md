
# 🧑‍💻 Easy Text Humanizer

Paste in any bloated or AI-ish content, and get back a cleaner, more natural human version.

This project includes:
- A **FastAPI backend** using OpenAI's `gpt-4o-mini` to rewrite and simplify text.
- A **lightweight HTML frontend** for quick, no-frills use.


## Demo

> Want to try it live? https://easy-text-humanizer-v1.pages.dev/

---

## Features

- Cleans up AI-like or corporate-style writing
- Removes:
  - Rhetorical templates
  - Buzzwords (like “synergy”, “cutting-edge”)
  - Em-dashes and stacked adjectives
  - Filler words like “Honestly…”
- Flags remaining issues post-rewrite (linting)
- Simple dropdown for language hint (auto, English, Spanish)
- One-click clipboard copy of the output
- Fast and lightweight — no frameworks on the frontend

---

## Deployment

Frontend is deployed via Cloudflare Pages
🔗 https://easy-text-humanizer-v1.pages.dev

Backend is deployed using Cloudflare Workers
🔗 https://humanizer-007.nohemygraffe.workers.dev/api/humanize

The frontend calls the backend via /api/humanize, which connects to the Cloudflare Worker deployment running your FastAPI logic.

---

## Tech stack

- **Frontend:** HTML + vanilla JS
- **Backend:** FastAPI + Python
- **AI Model:** `gpt-4o-mini` via OpenAI API
- **Linting:** Regex-based content checks
- **CORS:** Fully enabled for development

