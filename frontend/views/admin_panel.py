import tkinter as tk
from tkinter import ttk
from frontend.api_client import api_client
from frontend.styles import COLORS


class AdminPanelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg=COLORS["bg"])
        self.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stats_frame = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.stats_frame, text="  Statistics  ")

        self.users_frame = tk.Frame(notebook, bg=COLORS["bg"])
        notebook.add(self.users_frame, text="  Users  ")

        self._build_stats()
        self._build_users()

    def _build_stats(self):
        status, data = api_client.get("/stats/")
        if status == 200:
            stats_cards = [
                ("\U0001F4DA", "Total Books", data.get("total_books", 0), COLORS["primary"]),
                ("\U0001F465", "Total Users", data.get("total_users", 0), COLORS["success"]),
                ("\U0001F4CB", "Reservations", data.get("total_reservations", 0), COLORS["warning"]),
                ("\u23F3", "Pending", data.get("pending_reservations", 0), COLORS["danger"]),
            ]

            cards_frame = tk.Frame(self.stats_frame, bg=COLORS["bg"])
            cards_frame.pack(fill=tk.X, padx=15, pady=15)

            for i, (icon, label, value, color) in enumerate(stats_cards):
                card = tk.Frame(cards_frame, bg="white", highlightbackground=COLORS["card_border"], highlightthickness=1)
                card.grid(row=0, column=i, padx=8, sticky="nsew")
                cards_frame.grid_columnconfigure(i, weight=1)

                tk.Label(card, text=icon, font=("Segoe UI", 28), bg="white", fg=color).pack(pady=(15, 0))
                tk.Label(card, text=str(value), font=("Segoe UI", 32, "bold"), bg="white", fg=color).pack()
                tk.Label(card, text=label, font=("Segoe UI", 10), bg="white", fg=COLORS["text_secondary"]).pack(pady=(0, 15))

            cats = data.get("categories", {})
            if cats:
                cat_frame = tk.Frame(self.stats_frame, bg="white", highlightbackground=COLORS["card_border"], highlightthickness=1)
                cat_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
                tk.Label(cat_frame, text="\U0001F4CA  Books by Category", font=("Segoe UI", 12, "bold"),
                         bg="white", fg=COLORS["text_primary"]).pack(anchor="w", padx=15, pady=(10, 5))
                sep = tk.Frame(cat_frame, bg=COLORS["card_border"], height=1)
                sep.pack(fill=tk.X, padx=15)
                for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                    row = tk.Frame(cat_frame, bg="white")
                    row.pack(fill=tk.X, padx=20, pady=3)
                    tk.Label(row, text=cat.capitalize(), font=("Segoe UI", 10), bg="white", fg=COLORS["text_primary"]).pack(side=tk.LEFT)
                    tk.Label(row, text=str(count), font=("Segoe UI", 10, "bold"), bg="white", fg=COLORS["primary"]).pack(side=tk.RIGHT)
                    bar = tk.Frame(row, bg=COLORS["primary_light"], height=6)
                    bar.pack(fill=tk.X, pady=2)
                    inner = tk.Frame(bar, bg=COLORS["primary"], width=int(count * 30))
                    inner.pack(side=tk.LEFT, fill=tk.Y)

    def _build_users(self):
        toolbar = tk.Frame(self.users_frame, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(toolbar, text="\u21bb Refresh", bg=COLORS["primary"], fg="white", font=("Segoe UI", 9),
                  border=0, padx=12, pady=4, cursor="hand2", command=self._refresh_users).pack(side=tk.LEFT, padx=8, pady=8)
        tk.Button(toolbar, text="\u2716 Delete Selected", bg=COLORS["danger"], fg="white", font=("Segoe UI", 9),
                  border=0, padx=12, pady=4, cursor="hand2", command=self._delete_user).pack(side=tk.LEFT, padx=8, pady=8)

        columns = ("id", "username", "email", "role", "active")
        self.user_tree = ttk.Treeview(self.users_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "username": "Username", "email": "Email", "role": "Role", "active": "Active"}
        for col in columns:
            self.user_tree.heading(col, text=headings[col])
            self.user_tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        self._refresh_users()

    def _refresh_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        status, data = api_client.get("/admin/users/")
        if status == 200:
            for u in data:
                self.user_tree.insert("", tk.END, values=(u["id"], u["username"], u["email"], u["role"], "Yes" if u["is_active"] else "No"))

    def _delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            return
        values = self.user_tree.item(selected[0], "values")
        user_id, username = values[0], values[1]
        confirm = tk.messagebox.askyesno("Confirm Delete", f"Delete user \"{username}\" (ID: {user_id})?")
        if not confirm:
            return
        status, _ = api_client.delete(f"/admin/users/{user_id}")
        if status == 204:
            self._refresh_users()
        else:
            tk.messagebox.showerror("Error", "Failed to delete user.")
