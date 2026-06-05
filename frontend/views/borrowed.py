import tkinter as tk
from tkinter import ttk
from frontend.api_client import api_client


class BorrowedBooksView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="  Your borrowed books — return them physically to the library before the due date!", font=("Segoe UI", 9), foreground="#7f8c8d").pack(side=tk.LEFT, padx=10)

        columns = ("id", "book", "borrowed", "due", "days_left", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book Title", "borrowed": "Borrowed Date", "due": "Due Date", "days_left": "Days Left", "status": "Status"}
        widths = {"id": 40, "book": 300, "borrowed": 130, "due": 130, "days_left": 90, "status": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])

        self.tree.tag_configure("overdue", background="#fce4e4")
        self.tree.tag_configure("warning", background="#fff9e6")
        self.tree.tag_configure("ok", background="#e8f5e9")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

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
                    status_text = "Overdue!"
                elif days <= 3:
                    tag = "warning"
                    status_text = f"{days} days left"
                self.tree.insert("", tk.END, values=(
                    b["id"], b.get("book_title", ""), borrowed_str, due_str,
                    days, status_text,
                ), tags=(tag,))
