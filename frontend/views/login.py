"""
Login and Registration view for the Tkinter frontend.

Provides a tabbed interface where users can log in with
existing credentials or register a new account.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client


class LoginView(tk.Frame):
    """
    Frame containing login and register tabs.

    On successful authentication the view calls the
    on_login_success callback so the parent can switch
    to the main dashboard.
    """

    def __init__(self, parent: tk.Frame, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # ---------- Login tab ----------
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="Login")

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.login_password = ttk.Entry(login_frame, show="*", width=30)
        self.login_password.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(login_frame, text="Login", command=self._login).grid(row=2, column=0, columnspan=2, pady=15)

        # ---------- Register tab ----------
        reg_frame = ttk.Frame(notebook)
        notebook.add(reg_frame, text="Register")

        ttk.Label(reg_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.reg_username = ttk.Entry(reg_frame, width=30)
        self.reg_username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(reg_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.reg_email = ttk.Entry(reg_frame, width=30)
        self.reg_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(reg_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.reg_password = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_password.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(reg_frame, text="Confirm Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.reg_confirm = ttk.Entry(reg_frame, show="*", width=30)
        self.reg_confirm.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(reg_frame, text="Register", command=self._register).grid(row=4, column=0, columnspan=2, pady=15)

        # Allow pressing Enter to login
        self.login_password.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        if not username or not password:
            messagebox.showwarning("Validation", "Please enter username and password.")
            return

        status, data = api_client.post("/auth/login", {"username": username, "password": password})
        if status == 200:
            api_client.token = data["access_token"]
            self.on_login_success()
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

        status, data = api_client.post(
            "/auth/register",
            {"username": username, "email": email, "password": password},
        )
        if status == 201:
            messagebox.showinfo("Success", "Account created. You can now log in.")
        else:
            detail = data.get("detail", "Registration failed")
            messagebox.showerror("Registration Error", detail)
