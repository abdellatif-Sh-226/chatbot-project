import tkinter as tk
from frontend.config import APP_TITLE, APP_GEOMETRY
from frontend.views.login import LoginView
from frontend.views.dashboard import DashboardView
from frontend.styles import COLORS


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.resizable(True, True)
        self.configure(bg=COLORS["bg"])
        self.minsize(900, 600)

        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self._current_view = None
        self._show_login()

    def _clear(self):
        if self._current_view:
            self._current_view.pack_forget()
            self._current_view.destroy()
            self._current_view = None

    def _show_login(self):
        self._clear()
        self._current_view = LoginView(self.container, on_login_success=self._show_dashboard)

    def _show_dashboard(self, role="member"):
        self._clear()
        self._current_view = DashboardView(self.container, on_logout=self._show_login, user_role=role)


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
