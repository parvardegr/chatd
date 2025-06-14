import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".chatd" / "config.json"
DEFAULT_CONFIG = {
    "system_prompt": "Your name is chatd. You are a helpful assistant.",
    "openai_base_url": "https://api.openai.com/v1",
    "api_key": ""
}

def load_config():
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

CHAT_DIR = Path.home() / ".chatd" / "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

CHATS_LIST_PATH = Path.home() / ".chatd" / "chats" / "list"

def load_chats():
    if not CHATS_LIST_PATH.exists():
        with CHATS_LIST_PATH.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    with CHATS_LIST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_chats(chats_list):
    with CHATS_LIST_PATH.open("w", encoding="utf-8") as f:
        json.dump(chats_list, f, indent=2)

def delete_chat(uid: str):
    chat_file_path = CHAT_DIR / f"{uid}.json"
    if chat_file_path.exists():
        chat_file_path.delete()

    # update chats list
    chats_list = load_chats()
    chats_list = [item for item in data if item["id"] != uid]
    save_chats(chats_list)

def load_chat(uid: str):
    for fname in os.listdir(CHAT_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(CHAT_DIR, fname)) as f:
                chats = json.load(f)

def create_chat():
    pass
