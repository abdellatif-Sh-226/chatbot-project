import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client


class BorrowRequestsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Confirm Pickup", command=self._pickup).pack(side=tk.LEFT, padx=2)
        ttk.Label(toolbar, text="  Mark as picked up when the user collects the book", font=("Segoe UI", 9), foreground="#7f8c8d").pack(side=tk.LEFT, padx=10)

        columns = ("id", "book", "user", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book Title", "user": "User", "created": "Accepted At"}
        widths = {"id": 40, "book": 300, "user": 150, "created": 150}
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
        status, data = api_client.get("/reservations/accepted")
        if status == 200:
            for r in data:
                self.tree.insert("", tk.END, values=(
                    r["id"], r.get("book_title", ""), r.get("username", ""),
                    r["created_at"][:10] if r.get("created_at") else "",
                ))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a request first")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _pickup(self):
        rid = self._get_selected()
        if not rid:
            return
        if messagebox.askyesno("Confirm Pickup", "Confirm that the user picked up this book?"):
            status, data = api_client.post(f"/reservations/{rid}/pickup", {})
            if status == 200:
                messagebox.showinfo("Success", "Pickup confirmed! Book is now in user's My Books.")
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed"))
