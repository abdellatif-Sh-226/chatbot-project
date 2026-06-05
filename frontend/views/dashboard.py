import tkinter as tk
from frontend.api_client import api_client
from frontend.styles import COLORS
from frontend.views.books import BooksView
from frontend.views.chat import ChatView
from frontend.views.reservations import ReservationsView
from frontend.views.admin_panel import AdminPanelView
from frontend.views.borrowed import BorrowedBooksView
from frontend.views.borrow_requests import BorrowRequestsView
from frontend.views.admin_borrowed import AdminBorrowedView


NAV_ITEMS = [
    ("Books", "books", "\U0001F4DA"),
    ("member", [
        ("My Books", "borrowed", "\U0001F4D6"),
        ("Reservations", "reservations", "\U0001F4CB"),
    ]),
    ("admin", [
        ("Reservations", "reservations", "\U0001F4CB"),
        ("Borrow Requests", "borrow_requests", "\U00002753"),
        ("Borrowed Books", "admin_borrowed", "\U0001F4D5"),
        ("Admin Panel", "admin", "\U00002699\U0000FE0F"),
    ]),
    ("Chatbot", "chat", "\U0001F916"),
]


class DashboardView(tk.Frame):
    def __init__(self, parent, on_logout, user_role="member"):
        super().__init__(parent)
        self.on_logout = on_logout
        self.user_role = user_role
        self._nav_labels = []
        self._current_view_name = None
        self.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        header_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        header_frame.pack(fill=tk.X, pady=(20, 10))
        tk.Label(header_frame, text="\U0001F3EB", font=("Segoe UI", 24), bg=COLORS["sidebar_bg"], fg="white").pack()
        tk.Label(header_frame, text="Smart Library", font=("Segoe UI", 14, "bold"), bg=COLORS["sidebar_bg"], fg="white").pack()
        tk.Label(header_frame, text="Management System", font=("Segoe UI", 9), bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"]).pack()

        sep = tk.Frame(sidebar, bg=COLORS["sidebar_active_bg"], height=1)
        sep.pack(fill=tk.X, padx=15, pady=10)

        nav_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        nav_frame.pack(fill=tk.BOTH, expand=True)

        self._build_nav(nav_frame)

        sep2 = tk.Frame(sidebar, bg=COLORS["sidebar_active_bg"], height=1)
        sep2.pack(fill=tk.X, padx=15, pady=5)

        logout_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        logout_frame.pack(fill=tk.X, pady=(5, 15))
        logout_btn = tk.Label(logout_frame, text="\U0001F6AA  Logout", fg=COLORS["danger"], bg=COLORS["sidebar_bg"],
                              font=("Segoe UI", 11), anchor="w", padx=25, pady=10, cursor="hand2")
        logout_btn.pack(fill=tk.X)
        logout_btn.bind("<Button-1>", lambda e: self._logout())
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg=COLORS["sidebar_active_bg"]))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg=COLORS["sidebar_bg"]))

        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._show_view("books")

    def _build_nav(self, parent):
        for item in NAV_ITEMS:
            if isinstance(item, tuple) and len(item) == 3 and isinstance(item[1], str):
                label, view_name, icon = item
                if view_name == "books" or (isinstance(item[0], str) and item[0] == "Chatbot"):
                    self._add_nav_btn(parent, f"{icon}  {label}", view_name)
                continue

            if isinstance(item, tuple) and len(item) == 2:
                role, items = item
                if role == self.user_role or role == "all":
                    for label, view_name, icon in items:
                        self._add_nav_btn(parent, f"    {icon}  {label}", view_name)

    def _add_nav_btn(self, parent, text, view_name):
        btn = tk.Label(parent, text=text, bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"],
                       font=("Segoe UI", 11), anchor="w", padx=25, pady=10, cursor="hand2")
        btn.pack(fill=tk.X)
        btn.bind("<Button-1>", lambda e, v=view_name: self._show_view(v))
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["sidebar_active_bg"], fg=COLORS["sidebar_active_fg"]) if self._current_view_name != view_name else None)
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"]) if self._current_view_name != view_name else None)
        self._nav_labels.append((btn, view_name))

    def _show_view(self, name):
        if self._current_view_name == name:
            return
        self._current_view_name = name

        for btn, vn in self._nav_labels:
            if vn == name:
                btn.config(bg=COLORS["primary"], fg="white")
            else:
                btn.config(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_fg"])

        for widget in self.content.winfo_children():
            widget.destroy()

        views = {
            "books": lambda: BooksView(self.content, user_role=self.user_role),
            "borrowed": lambda: BorrowedBooksView(self.content),
            "reservations": lambda: ReservationsView(self.content, is_admin=(self.user_role == "admin")),
            "borrow_requests": lambda: BorrowRequestsView(self.content),
            "admin_borrowed": lambda: AdminBorrowedView(self.content),
            "chat": lambda: ChatView(self.content),
            "admin": lambda: AdminPanelView(self.content) if self.user_role == "admin" else None,
        }
        view_fn = views.get(name)
        if view_fn:
            view_fn()

    def _logout(self):
        api_client.token = None
        for widget in self.winfo_children():
            widget.destroy()
        self.pack_forget()
        self.on_logout()
