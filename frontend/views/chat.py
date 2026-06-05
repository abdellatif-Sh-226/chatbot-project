import tkinter as tk
import threading
import queue
from tkinter import ttk, scrolledtext
from frontend.api_client import api_client
from frontend.styles import COLORS


class ChatView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg=COLORS["bg"])
        self.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        tk.Label(header, text="\U0001F916  Library Chatbot", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=15, pady=12)
        tk.Label(header, text="Ask me anything about books!", font=("Segoe UI", 9),
                 bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=5)

        chat_frame = tk.Frame(self, bg="white", highlightbackground=COLORS["card_border"], highlightthickness=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_area = tk.Text(
            chat_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=("Segoe UI", 10), bg="#fafafa", fg=COLORS["text_primary"],
            padx=15, pady=10, border=0, relief=tk.FLAT,
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.chat_area.tag_config("user", foreground=COLORS["primary"], font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("bot", foreground=COLORS["text_primary"], font=("Segoe UI", 10))
        self.chat_area.tag_config("system", foreground=COLORS["text_muted"], font=("Segoe UI", 9, "italic"))
        self.chat_area.tag_config("user_prefix", foreground=COLORS["primary"], font=("Segoe UI", 9, "bold"))
        self.chat_area.tag_config("bot_prefix", foreground=COLORS["success"], font=("Segoe UI", 9, "bold"))
        self.chat_area.tag_config("bot_bubble", background="#f0f7ff", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_area.tag_config("user_bubble", background="#e8f5e9", lmargin1=10, lmargin2=10, rmargin=10)

        input_area = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        input_area.pack(fill=tk.X, padx=10, pady=(0, 10))

        inner = tk.Frame(input_area, bg=COLORS["card_bg"], padx=10, pady=10)
        inner.pack(fill=tk.X)

        self.message_var = tk.StringVar()
        self.entry = ttk.Entry(inner, textvariable=self.message_var, font=("Segoe UI", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._send_message())

        self.send_btn = tk.Button(inner, text="\U000027A1  Send", bg=COLORS["primary"], fg="white",
                                   font=("Segoe UI", 10, "bold"), border=0, padx=16, pady=6,
                                   cursor="hand2", activebackground=COLORS["primary_hover"],
                                   activeforeground="white", command=self._send_message)
        self.send_btn.pack(side=tk.RIGHT)

        self._result_queue = queue.Queue()
        self._poll_queue()

        self._append_system("Welcome to the Library Chatbot! Ask me about books, authors, or recommendations.")

    def _append_message(self, text, tag):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text + "\n\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _append_system(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\U0001F539 {text}\n\n", "system")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _append_user(self, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\U0001F464  You\n", "user_prefix")
        self.chat_area.insert(tk.END, f"{text}\n\n", "user")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _append_bot(self, text, source=""):
        self.chat_area.config(state=tk.NORMAL)
        prefix = "\U0001F916  SmartLib" if not source or source == "ai" else f"\U0001F916  SmartLib ({source})"
        self.chat_area.insert(tk.END, f"{prefix}\n", "bot_prefix")
        self.chat_area.insert(tk.END, f"{text}\n\n", "bot")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _poll_queue(self):
        try:
            while True:
                result = self._result_queue.get_nowait()
                kind, payload = result
                if kind == "ok":
                    status, data = payload
                    self._handle_chat_response(status, data)
                elif kind == "error":
                    self._append_bot(f"Connection error: {payload}")
                    self._re_enable_send()
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _send_message(self):
        message = self.message_var.get().strip()
        if not message:
            return
        self.message_var.set("")
        self._append_user(message)
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._do_chat_request, args=(message,), daemon=True).start()

    def _do_chat_request(self, message):
        try:
            status, data = api_client.post("/chat/", {"message": message})
            self._result_queue.put(("ok", (status, data)))
        except Exception as e:
            self._result_queue.put(("error", str(e)))

    def _handle_chat_response(self, status, data):
        if status == 200:
            reply = data.get("reply", "No response.")
            source = data.get("source", "")
            self._append_bot(reply, source)
        else:
            detail = data.get("detail", "Chat request failed.")
            self._append_bot(f"Error: {detail}")
        self._re_enable_send()

    def _re_enable_send(self):
        self.send_btn.config(state=tk.NORMAL)
        self.entry.focus_set()
