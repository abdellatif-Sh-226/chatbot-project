import tkinter as tk
from frontend.api_client import api_client
from frontend.views.books import BooksView
from frontend.views.chat import ChatView
from frontend.views.reservations import ReservationsView
from frontend.views.admin_panel import AdminPanelView
from frontend.views.borrowed import BorrowedBooksView
from frontend.views.borrow_requests import BorrowRequestsView
from frontend.views.admin_borrowed import AdminBorrowedView


class DashboardView(tk.Frame):
    def __init__(self, parent, on_logout, user_role="member"):
        super().__init__(parent)
        self.on_logout = on_logout
        self.user_role = user_role
        self.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(self, width=200, bg="#2c3e50")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Library System", fg="white", bg="#2c3e50", font=("Segoe UI", 14, "bold"), pady=20).pack(fill=tk.X)

        nav_style = {"fg": "white", "bg": "#2c3e50", "font": ("Segoe UI", 11), "anchor": "w", "padx": 20, "pady": 8, "cursor": "hand2"}

        def nav(label, view_name):
            btn = tk.Label(sidebar, text=f"  {label}", **nav_style)
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e: self._show_view(view_name))

        nav("Books", "books")

        if self.user_role == "admin":
            nav("Reservations", "reservations")
            nav("Borrow Requests", "borrow_requests")
            nav("Borrowed Books", "admin_borrowed")
            nav("Admin Panel", "admin")
        else:
            nav("My Books", "borrowed")
            nav("Reservations", "reservations")

        nav("Chatbot", "chat")

        tk.Label(sidebar, text="", bg="#2c3e50").pack(expand=True)
        logout_btn = tk.Label(sidebar, text="  Logout", fg="#e74c3c", bg="#2c3e50", font=("Segoe UI", 11), anchor="w", padx=20, pady=8, cursor="hand2")
        logout_btn.pack(fill=tk.X)
        logout_btn.bind("<Button-1>", lambda e: self._logout())

        self.content = tk.Frame(self, bg="#ecf0f1")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._current_view = None
        self._show_view("books")

    def _show_view(self, name):
        if self._current_view == name:
            return
        self._current_view = name
        for widget in self.content.winfo_children():
            widget.destroy()
        if name == "books":
            BooksView(self.content, user_role=self.user_role)
        elif name == "borrowed":
            BorrowedBooksView(self.content)
        elif name == "reservations":
            ReservationsView(self.content, is_admin=(self.user_role == "admin"))
        elif name == "borrow_requests":
            BorrowRequestsView(self.content)
        elif name == "admin_borrowed":
            AdminBorrowedView(self.content)
        elif name == "chat":
            ChatView(self.content)
        elif name == "admin" and self.user_role == "admin":
            AdminPanelView(self.content)

    def _logout(self):
        api_client.token = None
        for widget in self.winfo_children():
            widget.destroy()
        self.pack_forget()
        self.on_logout()
