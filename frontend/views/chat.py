"""
Chatbot view for the Tkinter frontend.

Provides a chat-style interface where the user can type
natural-language questions about the library and receive
AI-generated answers.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from frontend.api_client import api_client


class ChatView(tk.Frame):
    """A messenger-style chatbot panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Chat display (read-only)
        self.chat_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, state=tk.DISABLED,
            font=("Segoe UI", 10), bg="#f5f5f5",
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))

        # Tag styles for user / bot messages
        self.chat_area.tag_config("user", foreground="#1a73e8", font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("bot", foreground="#333333", font=("Segoe UI", 10))
        self.chat_area.tag_config("system", foreground="#999999", font=("Segoe UI", 9, "italic"))
        self.chat_area.tag_config("source_tag", foreground="#888888", font=("Segoe UI", 8))

        # Input area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.message_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, textvariable=self.message_var, font=("Segoe UI", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self._send_message())

        self.send_btn = ttk.Button(input_frame, text="Send", command=self._send_message)
        self.send_btn.pack(side=tk.RIGHT)

        self._append_system("Welcome to the Library Chatbot! Ask me about books.")

    def _append_message(self, text: str, tag: str):
        """Insert a message into the chat scrollable text area."""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text + "\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _append_system(self, text: str):
        self._append_message(f"🔹 {text}", "system")

    def _append_user(self, text: str):
        self._append_message(f"You: {text}", "user")

    def _append_bot(self, text: str, source: str = ""):
        prefix = "Bot" if not source or source == "ai" else f"Bot ({source})"
        self._append_message(f"{prefix}: {text}", "bot")

    def _send_message(self):
        """Send the user's message to the chatbot API."""
        message = self.message_var.get().strip()
        if not message:
            return

        self.message_var.set("")
        self._append_user(message)
        self.send_btn.config(state=tk.DISABLED)

        try:
            status, data = api_client.post("/chat/", {"message": message})
            if status == 200:
                reply = data.get("reply", "No response.")
                source = data.get("source", "")
                self._append_bot(reply, source)
            else:
                detail = data.get("detail", "Chat request failed.")
                self._append_bot(f"Error: {detail}")
        except Exception as e:
            self._append_bot(f"Connection error: {e}")
        finally:
            self.send_btn.config(state=tk.NORMAL)
            self.entry.focus_set()
