import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client


class ReservationsView(tk.Frame):
    def __init__(self, parent, is_admin=False):
        super().__init__(parent)
        self.is_admin = is_admin
        self.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)
        if is_admin:
            ttk.Button(toolbar, text="Accept", command=self._accept).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Reject", command=self._reject).pack(side=tk.LEFT, padx=2)

        columns = ("id", "book", "user", "status", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book", "user": "User", "status": "Status", "created": "Created"}
        widths = {"id": 40, "book": 250, "user": 120, "status": 100, "created": 150}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        endpoint = "/reservations/" if self.is_admin else "/reservations/me"
        status, data = api_client.get(endpoint)
        if status == 200:
            for r in data:
                self.tree.insert("", tk.END, values=(
                    r["id"], r.get("book_title", ""), r.get("username", ""),
                    r["status"], r["created_at"][:10] if r.get("created_at") else "",
                ))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a reservation first")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _accept(self):
        rid = self._get_selected()
        if rid:
            api_client.post(f"/reservations/{rid}/accept", {})
            self._refresh()

    def _reject(self):
        rid = self._get_selected()
        if rid:
            api_client.post(f"/reservations/{rid}/reject", {})
            self._refresh()
