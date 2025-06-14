# 🤖 chatbot — ChatGPT in Your Terminal

> An open-source terminal UI for ChatGPT, with file uploads, chat history, and blazing-fast UX.

## ✨ Features
- Multi-chat sidebar UI
- Markdown support
- File uploads with OpenAI Assistants
- Per-chat JSON storage
- Customizable settings (model, base URL)
- One-line install: `curl -s https://... | bash`

## 📦 Installation

```bash
curl -s https://raw.githubusercontent.com/<your-org>/chatbot/main/assets/install.sh | bash


## TODO
- ctrl+n for '+new chat' shortcut
- add tools like web search, global memory, selectable deep think using deep think models
- make the app works without any mouse, all features most work using a keyboard
- add more models

##
uv venv
source .venv/bin/activate
uv pip install --upgrade pip
uv init --name chatd



# run
uv run app.main
