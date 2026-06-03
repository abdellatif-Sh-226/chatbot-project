"""
Frontend entry point.

Launches the Tkinter main window. Shows the login view
first, then switches to the dashboard on success.
"""

import tkinter as tk
from frontend.config import APP_TITLE, APP_GEOMETRY
from frontend.views.login import LoginView
from frontend.views.dashboard import DashboardView


class Application(tk.Tk):
    """
    Root Tkinter application window.

    Manages a single container that swaps between the
    login view and the main dashboard.
    """

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.resizable(True, True)

        # Container frame that holds the current view
        self.container = tk.Frame(self)
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

    def _show_dashboard(self):
        self._clear()
        self._current_view = DashboardView(self.container, on_logout=self._show_login)


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
