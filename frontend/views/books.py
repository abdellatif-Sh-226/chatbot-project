"""
Book management view for the Tkinter frontend.

Displays a searchable, paginated table of books and
provides Add / Edit / Delete dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from frontend.api_client import api_client


class BookDialog(tk.Toplevel):
    """Modal dialog for creating or editing a book."""

    def __init__(self, parent, title="Book", book=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.book = book

        fields = ["titre", "auteur", "categorie", "annee_publication", "quantite_disponible", "statut"]
        self.entries = {}

        for i, field in enumerate(fields):
            ttk.Label(self, text=field.replace("_", " ").title() + ":").grid(row=i, column=0, padx=5, pady=3, sticky="e")
            entry = ttk.Entry(self, width=35)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.entries[field] = entry

        # Pre-fill values when editing
        if book:
            self.entries["titre"].insert(0, book.get("titre", ""))
            self.entries["auteur"].insert(0, book.get("auteur", ""))
            self.entries["categorie"].insert(0, book.get("categorie", ""))
            self.entries["annee_publication"].insert(0, str(book.get("annee_publication") or ""))
            self.entries["quantite_disponible"].insert(0, str(book.get("quantite_disponible", 0)))
            self.entries["statut"].insert(0, book.get("statut", "disponible"))

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set()
        self.wait_window()

    def _save(self):
        data = {}
        for field, entry in self.entries.items():
            val = entry.get().strip()
            if field == "annee_publication":
                data[field] = int(val) if val else None
            elif field == "quantite_disponible":
                data[field] = int(val) if val else 0
            else:
                data[field] = val

        if not data.get("titre") or not data.get("auteur"):
            messagebox.showwarning("Validation", "Title and author are required.")
            return

        self.result = data
        self.destroy()


class BooksView(tk.Frame):
    """Main book management panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="+ Add Book", command=self._add_book).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit", command=self._edit_book).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete", command=self._delete_book).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Go", command=self._search).pack(side=tk.LEFT, padx=2)
        search_entry.bind("<Return>", lambda e: self._search())

        # Table
        columns = ("id", "titre", "auteur", "categorie", "annee", "qte", "statut")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "titre": "Title", "auteur": "Author", "categorie": "Category",
                     "annee": "Year", "qte": "Qty", "statut": "Status"}
        widths = {"id": 50, "titre": 250, "auteur": 200, "categorie": 120, "annee": 70, "qte": 50, "statut": 100}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col in ("id", "annee", "qte") else "w")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self._refresh()

    def _refresh(self):
        """Reload all books from the API."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        status, data = api_client.get("/books/")
        if status == 200:
            for book in data:
                self.tree.insert("", tk.END, values=(
                    book["id_livre"],
                    book["titre"],
                    book["auteur"],
                    book["categorie"],
                    book["annee_publication"] or "",
                    book["quantite_disponible"],
                    book["statut"],
                ))

    def _search(self):
        """Search books and display results in the table."""
        query = self.search_var.get().strip()
        if not query:
            self._refresh()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        endpoint = f"/books/search?query={query}"
        status, data = api_client.get(endpoint)
        if status == 200:
            for book in data:
                self.tree.insert("", tk.END, values=(
                    book["id_livre"],
                    book["titre"],
                    book["auteur"],
                    book["categorie"],
                    book["annee_publication"] or "",
                    book["quantite_disponible"],
                    book["statut"],
                ))

    def _get_selected_book(self):
        """Return the selected book row or None."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a book first.")
            return None
        values = self.tree.item(sel[0], "values")
        return {
            "id_livre": int(values[0]),
            "titre": values[1],
            "auteur": values[2],
            "categorie": values[3],
            "annee_publication": int(values[4]) if values[4] else None,
            "quantite_disponible": int(values[5]),
            "statut": values[6],
        }

    def _add_book(self):
        dialog = BookDialog(self, title="Add Book")
        if dialog.result:
            status, data = api_client.post("/books/", dialog.result)
            if status == 201:
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed to add book"))

    def _edit_book(self):
        book = self._get_selected_book()
        if not book:
            return
        dialog = BookDialog(self, title="Edit Book", book=book)
        if dialog.result:
            status, data = api_client.put(f"/books/{book['id_livre']}", dialog.result)
            if status == 200:
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed to update book"))

    def _delete_book(self):
        book = self._get_selected_book()
        if not book:
            return
        if messagebox.askyesno("Confirm", f"Delete '{book['titre']}'?"):
            status, _ = api_client.delete(f"/books/{book['id_livre']}")
            if status == 204:
                self._refresh()
            else:
                messagebox.showerror("Error", "Failed to delete book")
