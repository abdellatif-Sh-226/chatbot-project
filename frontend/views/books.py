import io
import base64
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from frontend.api_client import api_client


MAX_PHOTO_SIZE = (200, 280)


class BookDialog(tk.Toplevel):
    def __init__(self, parent, title="Book", book=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.book = book
        self.photo_base64 = book.get("photo") if book else None

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

        photo_row = len(fields)
        ttk.Label(self, text="Photo:").grid(row=photo_row, column=0, padx=5, pady=3, sticky="e")
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=photo_row, column=1, padx=5, pady=3, sticky="w")
        ttk.Button(btn_frame, text="Choose Photo", command=self._choose_photo).pack(side=tk.LEFT, padx=(0, 10))
        self.photo_preview = ttk.Label(btn_frame, text="No photo", relief=tk.SUNKEN, anchor="center", width=25)
        self.photo_preview.pack(side=tk.LEFT)

        if self.photo_base64:
            self._show_preview(self.photo_base64)

        action_row = photo_row + 1
        btn_frame2 = ttk.Frame(self)
        btn_frame2.grid(row=action_row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame2, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        self.grab_set()
        self.wait_window()

    def _choose_photo(self):
        path = filedialog.askopenfilename(
            title="Select Book Cover",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if not path:
            return
        try:
            img = Image.open(path)
            img.thumbnail(MAX_PHOTO_SIZE, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            self.photo_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            self._show_preview(self.photo_base64)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def _show_preview(self, b64_str):
        try:
            img_bytes = base64.b64decode(b64_str)
            img = Image.open(io.BytesIO(img_bytes))
            img.thumbnail((120, 160), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.photo_preview.config(image=tk_img, text="")
            self.photo_preview.image = tk_img
        except Exception:
            self.photo_preview.config(image="", text="Invalid photo")

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
        data["photo"] = self.photo_base64
        self.result = data
        self.destroy()


class BooksView(tk.Frame):
    def __init__(self, parent, user_role="member"):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.current_page = 1
        self.user_role = user_role
        self._photo_tk_ref = None

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

        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned)
        columns = ("id", "titre", "auteur", "categorie", "annee", "qte", "statut")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "titre": "Title", "auteur": "Author", "categorie": "Category", "annee": "Year", "qte": "Qty", "statut": "Status"}
        widths = {"id": 50, "titre": 250, "auteur": 200, "categorie": 120, "annee": 70, "qte": 50, "statut": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col])
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(left_frame, stretch="always")

        right_frame = ttk.Frame(paned, width=220)
        ttk.Label(right_frame, text="Book Cover", font=("Segoe UI", 9, "bold")).pack(pady=(5, 5))
        self.photo_label = ttk.Label(right_frame, text="Select a book", anchor="center", background="white")
        self.photo_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        paned.add(right_frame)

        paginator = ttk.Frame(self)
        paginator.pack(fill=tk.X, padx=5, pady=5)
        self.page_label = ttk.Label(paginator, text="Page 1")
        self.page_label.pack(side=tk.RIGHT, padx=5)
        ttk.Button(paginator, text="Next", command=self._next_page).pack(side=tk.RIGHT, padx=2)
        ttk.Button(paginator, text="Prev", command=self._prev_page).pack(side=tk.RIGHT, padx=2)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
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
        try:
            status, data = api_client.get(self._build_url())
            if status == 200:
                books = data.get("books", [])
                for book in books:
                    self.tree.insert("", tk.END, values=(
                        book["id_livre"], book["titre"], book["auteur"],
                        book["categorie"], book.get("annee_publication") or "",
                        book["quantite_disponible"], book["statut"],
                    ))
                self.page_label.config(text=f"Page {data.get('page', 1)} / {data.get('total_pages', 1)} ({data.get('total', 0)} books)")
            else:
                detail = data.get("detail", "Unknown error")
                messagebox.showerror("API Error", f"Status {status}: {detail}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load books:\n{e}")

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

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.photo_label.config(text="Select a book", image="")
            self._photo_tk_ref = None
            return
        try:
            book_id = int(self.tree.item(sel[0], "values")[0])
            status, data = api_client.get(f"/books/{book_id}")
            if status == 200 and data.get("photo"):
                self._display_photo(data["photo"])
            else:
                self.photo_label.config(text="No photo", image="")
                self._photo_tk_ref = None
        except Exception as e:
            self.photo_label.config(text=f"Error: {e}", image="")
            self._photo_tk_ref = None

    def _display_photo(self, b64_str):
        try:
            img_bytes = base64.b64decode(b64_str)
            img = Image.open(io.BytesIO(img_bytes))
            img.thumbnail((200, 280), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.photo_label.config(image=tk_img, text="")
            self._photo_tk_ref = tk_img
        except Exception:
            self.photo_label.config(text="Invalid image", image="")
            self._photo_tk_ref = None

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
        status, data = api_client.get(f"/books/{book['id_livre']}")
        if status != 200:
            messagebox.showerror("Error", "Could not fetch book details")
            return
        dialog = BookDialog(self, title="Edit Book", book=data)
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
