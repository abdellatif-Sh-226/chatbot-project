import tkinter as tk
from tkinter import ttk
from frontend.api_client import api_client
from frontend.styles import COLORS


class BorrowedBooksView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg=COLORS["bg"])
        self.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        tk.Label(header, text="\U0001F4D6  My Borrowed Books", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=15, pady=12)
        tk.Label(header, text="Return books physically to the library before the due date!",
                 font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=5)

        ttk.Button(header, text="\u21bb Refresh", command=self._refresh).pack(side=tk.RIGHT, padx=10, pady=10)

        columns = ("id", "book", "borrowed", "due", "days_left", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book Title", "borrowed": "Borrowed Date", "due": "Due Date", "days_left": "Days Left", "status": "Status"}
        widths = {"id": 40, "book": 300, "borrowed": 130, "due": 130, "days_left": 90, "status": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])
        self.tree.tag_configure("overdue", background=COLORS["danger_light"])
        self.tree.tag_configure("warning", background=COLORS["warning_light"])
        self.tree.tag_configure("ok", background=COLORS["success_light"])
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        status, data = api_client.get("/borrowed/me")
        if status == 200:
            for b in data:
                days = b.get("days_remaining", 0)
                due_str = b.get("due_date", "")[:10] if b.get("due_date") else ""
                borrowed_str = b.get("borrowed_at", "")[:10] if b.get("borrowed_at") else ""
                tag = "ok"
                status_text = "Active"
                if days <= 0:
                    tag = "overdue"
                    status_text = "\u26A0 Overdue!"
                elif days <= 3:
                    tag = "warning"
                    status_text = f"{days} days left"
                self.tree.insert("", tk.END, values=(b["id"], b.get("book_title", ""), borrowed_str, due_str, days, status_text), tags=(tag,))
