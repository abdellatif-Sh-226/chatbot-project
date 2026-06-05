import tkinter as tk
from tkinter import ttk
from frontend.api_client import api_client


class AdminPanelView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="Statistics")
        self._build_stats()

        self.users_frame = ttk.Frame(notebook)
        notebook.add(self.users_frame, text="Users")
        self._build_users()

    def _build_stats(self):
        canvas = tk.Canvas(self.stats_frame, bg="#f5f5f5")
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        status, data = api_client.get("/stats/")
        if status == 200:
            stats = [
                ("Total Books", data.get("total_books", 0)),
                ("Total Users", data.get("total_users", 0)),
                ("Total Reservations", data.get("total_reservations", 0)),
                ("Pending Reservations", data.get("pending_reservations", 0)),
            ]
            row = 0
            for i in range(0, len(stats), 2):
                for j in range(2):
                    if i + j < len(stats):
                        label, val = stats[i + j]
                        frame = tk.Frame(canvas, bg="white", relief=tk.RIDGE, bd=1)
                        frame.grid(row=row, column=j, padx=10, pady=10, sticky="nsew")
                        tk.Label(frame, text=val, font=("Segoe UI", 24, "bold"), fg="#2c3e50", bg="white").pack(padx=30, pady=(15, 0))
                        tk.Label(frame, text=label, font=("Segoe UI", 10), fg="#7f8c8d", bg="white").pack(padx=30, pady=(0, 15))
                row += 1

            cats = data.get("categories", {})
            if cats:
                ttk.Label(canvas, text="Categories:", font=("Segoe UI", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w")
                row += 1
                for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                    ttk.Label(canvas, text=f"  {cat}: {count} books").grid(row=row, column=0, columnspan=2, sticky="w")
                    row += 1

    def _build_users(self):
        toolbar = ttk.Frame(self.users_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_users).pack(side=tk.LEFT, padx=2)

        columns = ("id", "username", "email", "role", "active")
        self.user_tree = ttk.Treeview(self.users_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "username": "Username", "email": "Email", "role": "Role", "active": "Active"}
        for col in columns:
            self.user_tree.heading(col, text=headings[col])
            self.user_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self._refresh_users()

    def _refresh_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        status, data = api_client.get("/admin/users/")
        if status == 200:
            for u in data:
                self.user_tree.insert("", tk.END, values=(
                    u["id"], u["username"], u["email"], u["role"], "Yes" if u["is_active"] else "No"
                ))
