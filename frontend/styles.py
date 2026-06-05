import tkinter as tk
from tkinter import ttk


COLORS = {
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_light": "#dbeafe",
    "success": "#16a34a",
    "success_light": "#dcfce7",
    "danger": "#dc2626",
    "danger_light": "#fee2e2",
    "warning": "#f59e0b",
    "warning_light": "#fef3c7",
    "sidebar_bg": "#1e293b",
    "sidebar_fg": "#cbd5e1",
    "sidebar_active_bg": "#334155",
    "sidebar_active_fg": "#ffffff",
    "bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "text_primary": "#0f172a",
    "text_secondary": "#64748b",
    "text_muted": "#94a3b8",
    "border": "#cbd5e1",
    "input_bg": "#f8fafc",
    "success_badge": "#16a34a",
    "danger_badge": "#dc2626",
    "warning_badge": "#f59e0b",
}


def setup_styles():
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=("Segoe UI", 10), background=COLORS["bg"], foreground=COLORS["text_primary"])

    style.configure("TButton", padding=(16, 8), relief="flat", background=COLORS["primary"], foreground="white", borderwidth=0, focuscolor="none")
    style.map("TButton", background=[("active", COLORS["primary_hover"]), ("disabled", COLORS["text_muted"])])

    style.configure("Secondary.TButton", background=COLORS["card_bg"], foreground=COLORS["primary"], relief="solid", borderwidth=1)
    style.map("Secondary.TButton", background=[("active", COLORS["primary_light"])])

    style.configure("Success.TButton", background=COLORS["success"])
    style.map("Success.TButton", background=[("active", "#15803d")])

    style.configure("Danger.TButton", background=COLORS["danger"])
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    style.configure("Toolbar.TFrame", background=COLORS["card_bg"], relief="solid", borderwidth=1)

    style.configure("Card.TFrame", background=COLORS["card_bg"], relief="solid", borderwidth=1)

    style.configure("Treeview", background=COLORS["card_bg"], foreground=COLORS["text_primary"], fieldbackground=COLORS["card_bg"], borderwidth=0, rowheight=32, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=COLORS["sidebar_bg"], foreground="white", relief="flat", font=("Segoe UI", 10, "bold"), padding=(8, 6))
    style.map("Treeview.Heading", background=[("active", COLORS["sidebar_active_bg"])])

    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text_primary"])
    style.configure("Card.TLabel", background=COLORS["card_bg"], foreground=COLORS["text_primary"])

    style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"), foreground=COLORS["text_primary"])

    style.configure("StatValue.TLabel", font=("Segoe UI", 28, "bold"), foreground=COLORS["primary"])
    style.configure("StatLabel.TLabel", font=("Segoe UI", 10), foreground=COLORS["text_secondary"])
    style.configure("StatSuccess.TLabel", font=("Segoe UI", 28, "bold"), foreground=COLORS["success"])
    style.configure("StatDanger.TLabel", font=("Segoe UI", 28, "bold"), foreground=COLORS["danger"])
    style.configure("StatWarning.TLabel", font=("Segoe UI", 28, "bold"), foreground=COLORS["warning"])

    style.configure("TEntry", fieldbackground=COLORS["input_bg"], borderwidth=1, relief="solid", padding=(8, 6))
    style.configure("TCombobox", fieldbackground=COLORS["input_bg"], borderwidth=1, relief="solid", padding=(6, 4))

    style.configure("TSpinbox", fieldbackground=COLORS["input_bg"], borderwidth=1, relief="solid", padding=(6, 4))

    style.configure("Sidebar.TFrame", background=COLORS["sidebar_bg"])
    style.configure("SidebarTitle.TLabel", background=COLORS["sidebar_bg"], foreground="white", font=("Segoe UI", 13, "bold"))
    style.configure("SidebarNav.TLabel", background=COLORS["sidebar_bg"], foreground=COLORS["sidebar_fg"], font=("Segoe UI", 11), padding=(20, 10))
    style.map("SidebarNav.TLabel", background=[("active", COLORS["sidebar_active_bg"])], foreground=[("active", COLORS["sidebar_active_fg"])])

    style.configure("SidebarLogout.TLabel", background=COLORS["sidebar_bg"], foreground=COLORS["danger"], font=("Segoe UI", 11), padding=(20, 10))
    style.map("SidebarLogout.TLabel", background=[("active", COLORS["sidebar_active_bg"])], foreground=[("active", COLORS["danger"])])

    style.configure("ChatUser.TLabel", foreground=COLORS["primary"], font=("Segoe UI", 10, "bold"), background=COLORS["bg"])
    style.configure("ChatBot.TLabel", foreground=COLORS["text_primary"], font=("Segoe UI", 10), background=COLORS["bg"])
    style.configure("ChatSystem.TLabel", foreground=COLORS["text_muted"], font=("Segoe UI", 9, "italic"), background=COLORS["bg"])

    style.configure("Badge.TLabel", font=("Segoe UI", 9, "bold"), padding=(6, 2))

    return style
