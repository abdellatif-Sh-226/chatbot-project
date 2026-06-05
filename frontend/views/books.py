import tkinter as tk
from tkinter import ttk, messagebox
from frontend.api_client import api_client


class BookDialog(tk.Toplevel):
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
    def __init__(self, parent, user_role="member"):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.current_page = 1
        self.user_role = user_role

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reserve", command=self._reserve_book).pack(side=tk.LEFT, padx=2)

        if self.user_role == "admin":
            ttk.Button(toolbar, text="+ Add Book", command=self._add_book).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Edit", command=self._edit_book).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Delete", command=self._delete_book).pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<Return>", lambda e: self._search())

        ttk.Label(toolbar, text="Category:").pack(side=tk.LEFT, padx=(10, 2))
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(toolbar, textvariable=self.cat_var, values=["", "roman", "science", "histoire", "informatique", "fiction"], width=12)
        self.cat_combo.pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text="Status:").pack(side=tk.LEFT, padx=(10, 2))
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(toolbar, textvariable=self.status_var, values=["", "disponible", "emprunté", "réservé"], width=12)
        self.status_combo.pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="Filter", command=self._search).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear", command=self._clear_filters).pack(side=tk.LEFT, padx=2)

        columns = ("id", "titre", "auteur", "categorie", "annee", "qte", "statut")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "titre": "Title", "auteur": "Author", "categorie": "Category", "annee": "Year", "qte": "Qty", "statut": "Status"}
        widths = {"id": 50, "titre": 250, "auteur": 200, "categorie": 120, "annee": 70, "qte": 50, "statut": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        paginator = ttk.Frame(self)
        paginator.pack(fill=tk.X, padx=5, pady=5)
        self.page_label = ttk.Label(paginator, text="Page 1")
        self.page_label.pack(side=tk.RIGHT, padx=5)
        ttk.Button(paginator, text="Next", command=self._next_page).pack(side=tk.RIGHT, padx=2)
        ttk.Button(paginator, text="Prev", command=self._prev_page).pack(side=tk.RIGHT, padx=2)

        self._refresh()

    def _build_url(self):
        params = [f"page={self.current_page}", "per_page=10"]
        if self.search_var.get().strip():
            params.append(f"query={self.search_var.get().strip()}")
        if self.cat_var.get():
            params.append(f"categorie={self.cat_var.get()}")
        if self.status_var.get():
            params.append(f"statut={self.status_var.get()}")
        return "/books/advanced?" + "&".join(params)

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        status, data = api_client.get(self._build_url())
        if status == 200:
            for book in data.get("books", []):
                self.tree.insert("", tk.END, values=(
                    book["id_livre"], book["titre"], book["auteur"],
                    book["categorie"], book.get("annee_publication") or "",
                    book["quantite_disponible"], book["statut"],
                ))
            self.page_label.config(text=f"Page {data.get('page', 1)} / {data.get('total_pages', 1)} ({data.get('total', 0)} books)")

    def _search(self):
        self.current_page = 1
        self._refresh()

    def _clear_filters(self):
        self.search_var.set("")
        self.cat_var.set("")
        self.status_var.set("")
        self.current_page = 1
        self._refresh()

    def _next_page(self):
        self.current_page += 1
        self._refresh()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._refresh()

    def _get_selected_book(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a book first.")
            return None
        values = self.tree.item(sel[0], "values")
        return {"id_livre": int(values[0]), "titre": values[1], "auteur": values[2], "categorie": values[3], "annee_publication": int(values[4]) if values[4] else None, "quantite_disponible": int(values[5]), "statut": values[6]}

    def _reserve_book(self):
        book = self._get_selected_book()
        if not book:
            return
        status, data = api_client.post("/reservations/", {"book_id": book["id_livre"]})
        if status == 201:
            messagebox.showinfo("Success", f"Reserved '{book['titre']}'!")
            self._refresh()
        else:
            messagebox.showerror("Error", data.get("detail", "Failed"))

    def _add_book(self):
        dialog = BookDialog(self, title="Add Book")
        if dialog.result:
            status, data = api_client.post("/books/", dialog.result)
            if status == 201:
                self._refresh()
            else:
                messagebox.showerror("Error", data.get("detail", "Failed"))

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
                messagebox.showerror("Error", data.get("detail", "Failed"))

    def _delete_book(self):
        book = self._get_selected_book()
        if not book:
            return
        if messagebox.askyesno("Confirm", f"Delete '{book['titre']}'?"):
            status, _ = api_client.delete(f"/books/{book['id_livre']}")
            if status == 204:
                self._refresh()
            else:
                messagebox.showerror("Error", "Failed to delete")
