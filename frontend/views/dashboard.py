"""
Main dashboard view.

Provides a sidebar navigation to switch between
Books management and Chatbot sections, plus a
logout button.
"""

import tkinter as tk
from tkinter import ttk
from frontend.api_client import api_client
from frontend.views.books import BooksView
from frontend.views.chat import ChatView


class DashboardView(tk.Frame):
    """
    Container that holds a sidebar (navigation) and a
    content area that swaps between views.
    """

    def __init__(self, parent, on_logout):
        super().__init__(parent)
        self.on_logout = on_logout
        self.pack(fill=tk.BOTH, expand=True)

        # ---------- Sidebar ----------
        sidebar = tk.Frame(self, width=200, bg="#2c3e50")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Library System",
            fg="white", bg="#2c3e50", font=("Segoe UI", 14, "bold"),
            pady=20,
        ).pack(fill=tk.X)

        nav_style = {"fg": "white", "bg": "#2c3e50", "font": ("Segoe UI", 11),
                      "anchor": "w", "padx": 20, "pady": 8, "cursor": "hand2"}

        self.btn_books = tk.Label(sidebar, text="  Books", **nav_style)
        self.btn_books.pack(fill=tk.X)
        self.btn_books.bind("<Button-1>", lambda e: self._show_view("books"))

        self.btn_chat = tk.Label(sidebar, text="  Chatbot", **nav_style)
        self.btn_chat.pack(fill=tk.X)
        self.btn_chat.bind("<Button-1>", lambda e: self._show_view("chat"))

        # Logout button at the bottom
        tk.Label(sidebar, text="", bg="#2c3e50").pack(expand=True)

        logout_btn = tk.Label(
            sidebar, text="  Logout", fg="#e74c3c", bg="#2c3e50",
            font=("Segoe UI", 11), anchor="w", padx=20, pady=8, cursor="hand2",
        )
        logout_btn.pack(fill=tk.X)
        logout_btn.bind("<Button-1>", lambda e: self._logout())

        # ---------- Content area ----------
        self.content = tk.Frame(self, bg="#ecf0f1")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._views = {}
        self._current_view = None
        self._show_view("books")

    def _show_view(self, name: str):
        """Swap the content area to the named view."""
        if self._current_view == name:
            return
        self._current_view = name

        # Clear content area
        for widget in self.content.winfo_children():
            widget.destroy()

        if name == "books":
            self._views[name] = BooksView(self.content)
        elif name == "chat":
            self._views[name] = ChatView(self.content)
        else:
            tk.Label(self.content, text="View not found", bg="#ecf0f1").pack()

    def _logout(self):
        """Clear the token and return to the login screen."""
        api_client.token = None
        for widget in self.winfo_children():
            widget.destroy()
        self.pack_forget()
        self.on_logout()
