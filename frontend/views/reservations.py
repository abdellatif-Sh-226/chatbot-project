import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client
from frontend.styles import COLORS


class ReservationsView(tk.Frame):
    def __init__(self, parent, is_admin=False):
        super().__init__(parent)
        self.is_admin = is_admin
        self.configure(bg=COLORS["bg"])
        self.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        title = "\U0001F4CB  All Reservations (Admin)" if is_admin else "\U0001F4CB  My Reservations"
        tk.Label(header, text=title, font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=15, pady=12)

        ttk.Button(header, text="\u21bb Refresh", command=self._refresh).pack(side=tk.RIGHT, padx=10, pady=10)
        if is_admin:
            ttk.Button(header, text="\U00002705 Accept", command=self._accept).pack(side=tk.RIGHT, padx=5, pady=10)
            ttk.Button(header, text="\U0000274C Reject", command=self._reject).pack(side=tk.RIGHT, padx=5, pady=10)

        columns = ("id", "book", "user", "status", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book", "user": "User", "status": "Status", "created": "Created"}
        widths = {"id": 40, "book": 250, "user": 120, "status": 100, "created": 150}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])
        self.tree.tag_configure("pending", foreground=COLORS["warning"])
        self.tree.tag_configure("accepted", foreground=COLORS["success"])
        self.tree.tag_configure("rejected", foreground=COLORS["danger"])
        self.tree.tag_configure("borrowed", foreground=COLORS["primary"])
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        endpoint = "/reservations/" if self.is_admin else "/reservations/me"
        status, data = api_client.get(endpoint)
        if status == 200:
            for r in data:
                tag = r["status"]
                self.tree.insert("", tk.END, values=(r["id"], r.get("book_title", ""), r.get("username", ""),
                    r["status"], r["created_at"][:10] if r.get("created_at") else ""), tags=(tag,))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a reservation first")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _accept(self):
        rid = self._get_selected()
        if rid:
            status, data = api_client.post(f"/reservations/{rid}/accept", {})
            if status == 200:
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed"))

    def _reject(self):
        rid = self._get_selected()
        if rid:
            status, data = api_client.post(f"/reservations/{rid}/reject", {})
            if status == 200:
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed"))
