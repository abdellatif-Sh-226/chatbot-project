import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client


class AdminBorrowedView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Return Book", command=self._return_book).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="  Search user:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<Return>", lambda e: self._refresh())

        columns = ("id", "book", "user", "borrowed", "due", "days_left")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "book": "Book Title", "user": "User", "borrowed": "Borrowed", "due": "Due Date", "days_left": "Days Left"}
        widths = {"id": 40, "book": 250, "user": 130, "borrowed": 120, "due": 120, "days_left": 90}
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
        status, data = api_client.get("/borrowed/all")
        if status == 200:
            search = self.search_var.get().strip().lower()
            for b in data:
                if search and search not in b.get("username", "").lower():
                    continue
                days = b.get("days_remaining", 0)
                tag = "ok"
                if days <= 0:
                    tag = "overdue"
                elif days <= 3:
                    tag = "warning"
                self.tree.insert("", tk.END, values=(
                    b["id"], b.get("book_title", ""), b.get("username", ""),
                    b.get("borrowed_at", "")[:10] if b.get("borrowed_at") else "",
                    b.get("due_date", "")[:10] if b.get("due_date") else "",
                    days,
                ), tags=(tag,))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a borrowed book first")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _return_book(self):
        bid = self._get_selected()
        if not bid:
            return
        if messagebox.askyesno("Confirm Return", "Mark this book as returned?"):
            status, data = api_client.post(f"/borrowed/{bid}/return", {})
            if status == 200:
                messagebox.showinfo("Success", "Book returned successfully!")
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed"))
