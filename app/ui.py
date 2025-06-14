from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Input, ListView, ListItem, Label, Button, TextArea
from textual.reactive import reactive
from textual.message import Message
from textual import events
from textual.containers import Container
from app.service import load_config, save_config, load_chats
from textual.screen import Screen

DUMMY_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "assistant", "content": "Hello! How can I help you?"},
    {"role": "user", "content": "Tell me a joke."},
]

DUMMY_CHATS = [
    {"id": "chat-1", "title": "First Chat", "system_prompt": "You are a helpful assistant."},
    {"id": "chat-2", "title": "Jokes Chat", "system_prompt": "You only tell jokes."},
]

# class Sidebar(Static):
#     def compose(self):
#         yield Label("Chats", id="sidebar-title")
#         self.chat_list = ListView(id="chat-list")  # NEW CHANGE
#         yield self.chat_list
#         self.load_chats()  # NEW CHANGE
#
#     def load_chats(self):  # NEW CHANGE
#         self.chat_list.clear()
#         for fname in os.listdir(CHAT_DIR):
#             if fname.endswith(".json"):
#                 with open(os.path.join(CHAT_DIR, fname)) as f:
#                     data = json.load(f)
#                 self.chat_list.append(ListItem(Label(data["title"]), id=fname))
#         self.chat_list.append(ListItem(Label("+ New Chat"), id="new-chat"))

class Sidebar(Static):
    def compose(self):
        yield Label("Chats", id="sidebar-title")

        with ListView(id="chat-list") as chat_list:
            yield ListItem(Label("+ New Chat"), id="new-chat")
            for chat in load_chats():
                yield ListItem(Label(chat["title"], id=chat["id"]))

class ChatMessages(Static):
    def __init__(self, messages, **kwargs):
        super().__init__(**kwargs)
        self.messages = messages

    def compose(self) -> ComposeResult:
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]
            prefix = {"user": "🧑", "assistant": "🤖", "system": "⚙️"}.get(role, "")
            yield Label(f"{prefix} {content}", classes=f"msg {role}")


class ChatInput(Static):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type your message...", id="chat-input")


class HotkeyBar(Static):
    def compose(self) -> ComposeResult:
        yield Label("Ctrl+B Toggle Sidebar | Ctrl+C Quit", id="hotkeys")

class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        self.config = load_config()

    def compose(self):
        with Container(id="settings-container"):
            yield Label("OpenAI API Key:")
            self.api_key_input = Input(value=self.config.get("api_key", ""), id="api-key-input")
            yield self.api_key_input

            yield Label("API Base URL:")
            self.api_url_input = Input(value=self.config.get("openai_base_url", ""), id="api-url-input")
            yield self.api_url_input

            yield Label("System Prompt:")
            self.system_prompt_input = TextArea(text=self.config.get("system_prompt", ""),id="system-prompt-input")
            yield self.system_prompt_input

            with Container(id="buttons-container"):
                with Horizontal(id="buttons-container"):
                    yield Button("Save", id="save-btn")
                    yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event):
        if event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "save-btn":
            self.config["api_key"] = self.api_key_input.value
            self.config["openai_base_url"] = self.api_url_input.value
            self.config["system_prompt"] = self.system_prompt_input.text
            save_config(self.config)
            self.app.pop_screen()

class ChatdApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+d", "delete_chat", "Delete Current Chat"),
        ("ctrl+s", "open_settings", "Settings"),
        ("ctrl+c", "quit", "Quit"),
    ]

    show_sidebar = reactive(True)

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_chat_id = None
        self.messages = []
        self.messages = list(DUMMY_MESSAGES)  # current chat messages

    def compose(self) -> ComposeResult:
        with Horizontal():
            self.sidebar = Sidebar(id="sidebar")
            yield self.sidebar

            with Vertical(id="main-area"):
                self.chat_messages = ChatMessages(self.messages, id="chat-messages")
                yield self.chat_messages

                self.chat_input = ChatInput(id="input")
                yield self.chat_input

                self.hotkey_bar = HotkeyBar(id="hotkey-bar")
                yield self.hotkey_bar

    def on_mount(self) -> None:
        self.set_layout_sizes()

    def on_resize(self, event) -> None:
        self.set_layout_sizes()

    def set_layout_sizes(self):
        width = self.size.width
        height = self.size.height

        sidebar_width = 30 if self.show_sidebar else 0
        main_width = width - sidebar_width

        # Sidebar size and visibility
        self.sidebar.styles.width = sidebar_width
        # self.sidebar.styles.height = height
        self.sidebar.visible = self.show_sidebar

        # Main area
        main_area = self.query_one("#main-area")
        main_area.styles.width = main_width
        main_area.styles.height = height

        input_height = 3
        hotkey_height = 1
        chat_height = height - (input_height + hotkey_height + 3)

        self.chat_messages.styles.height = chat_height
        self.chat_messages.styles.width = main_width

        # self.chat_input.styles.height = input_height
        self.chat_input.styles.width = main_width

        # self.hotkey_bar.styles.height = hotkey_height
        self.hotkey_bar.styles.width = main_width

        # Refresh layout
        self.sidebar.refresh(layout=True)
        main_area.refresh(layout=True)
        self.chat_messages.refresh(layout=True)
        self.chat_input.refresh(layout=True)
        self.hotkey_bar.refresh(layout=True)

    def watch_show_sidebar(self, visible: bool) -> None:
        if hasattr(self, "sidebar"):
            self.sidebar.visible = visible
            self.sidebar.refresh(layout=True)

    def action_toggle_sidebar(self) -> None:
        self.show_sidebar = not self.show_sidebar
        self.set_layout_sizes()

    def action_open_settings(self) -> None:
        self.push_screen(SettingsScreen())

    def action_delete_chat(self) -> None:
        if self.current_chat_id:
            delete_chat(self.current_chat_id)

        self.current_chat_id = None
        self.messages = []
        self.chat_messages.messages = self.messages
        self.chat_messages.refresh()
        self.sidebar.refresh()




