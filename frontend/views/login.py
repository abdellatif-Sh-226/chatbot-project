import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client
from frontend.styles import COLORS, setup_styles


class LoginView(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.role = "member"
        self.pack(fill=tk.BOTH, expand=True)

        setup_styles()

        self.configure(bg=COLORS["bg"])

        center = tk.Frame(self, bg=COLORS["bg"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(center, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        card.pack(padx=20, pady=20)

        tk.Label(card, text="\U0001F3EB", font=("Segoe UI", 36), bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(20, 5))
        tk.Label(card, text="Welcome to Smart Library", font=("Segoe UI", 18, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_primary"]).pack()
        tk.Label(card, text="Sign in to your account", font=("Segoe UI", 10), bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(pady=(0, 15))

        notebook = ttk.Notebook(card, style="TNotebook")
        notebook.pack(padx=30, pady=(0, 20))

        login_frame = ttk.Frame(notebook, padding=20)
        notebook.add(login_frame, text="  Login  ")

        ttk.Label(login_frame, text="Username").pack(anchor="w")
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(login_frame, text="Password").pack(anchor="w")
        self.login_password = ttk.Entry(login_frame, show="*", width=30)
        self.login_password.pack(fill=tk.X, pady=(2, 15))

        login_btn = tk.Button(login_frame, text="Sign In", bg=COLORS["primary"], fg="white",
                              font=("Segoe UI", 11, "bold"), padx=20, pady=6, border=0, cursor="hand2",
                              activebackground=COLORS["primary_hover"], activeforeground="white",
                              command=self._login)
        login_btn.pack(fill=tk.X)
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=COLORS["primary_hover"]))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=COLORS["primary"]))

        self.login_password.bind("<Return>", lambda e: self._login())

        reg_frame = ttk.Frame(notebook, padding=20)
        notebook.add(reg_frame, text="  Register  ")

        ttk.Label(reg_frame, text="Username").pack(anchor="w")
        self.reg_username = ttk.Entry(reg_frame, width=30)
        self.reg_username.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(reg_frame, text="Email").pack(anchor="w")
        self.reg_email = ttk.Entry(reg_frame, width=30)
        self.reg_email.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(reg_frame, text="Password").pack(anchor="w")
        self.reg_password = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_password.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(reg_frame, text="Confirm Password").pack(anchor="w")
        self.reg_confirm = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_confirm.pack(fill=tk.X, pady=(2, 15))

        reg_btn = tk.Button(reg_frame, text="Create Account", bg=COLORS["success"], fg="white",
                            font=("Segoe UI", 11, "bold"), padx=20, pady=6, border=0, cursor="hand2",
                            activebackground="#15803d", activeforeground="white",
                            command=self._register)
        reg_btn.pack(fill=tk.X)
        reg_btn.bind("<Enter>", lambda e: reg_btn.config(bg="#15803d"))
        reg_btn.bind("<Leave>", lambda e: reg_btn.config(bg=COLORS["success"]))

        tk.Label(card, text="Smart Library Management System v1.0", font=("Segoe UI", 8),
                 bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(pady=(0, 15))

    def _login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        if not username or not password:
            messagebox.showwarning("Validation", "Please enter username and password.")
            return
        status, data = api_client.post("/auth/login", {"username": username, "password": password})
        if status == 200:
            api_client.token = data["access_token"]
            import jwt
            try:
                payload = jwt.decode(data["access_token"], options={"verify_signature": False})
                role = payload.get("role", "member")
            except Exception:
                role = "member"
            self.on_login_success(role)
        else:
            detail = data.get("detail", "Login failed")
            messagebox.showerror("Login Error", detail)

    def _register(self):
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        if not username or not email or not password:
            messagebox.showwarning("Validation", "All fields are required.")
            return
        if password != confirm:
            messagebox.showwarning("Validation", "Passwords do not match.")
            return
        status, data = api_client.post("/auth/register", {"username": username, "email": email, "password": password})
        if status == 201:
            messagebox.showinfo("Success", "Account created. You can now log in.")
        else:
            detail = data.get("detail", "Registration failed")
            messagebox.showerror("Registration Error", detail)
