import io
import base64
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from frontend.api_client import api_client
from frontend.styles import COLORS, setup_styles


MAX_PHOTO_SIZE = (200, 280)


class BookDialog(tk.Toplevel):
    def __init__(self, parent, title="Book", book=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.book = book
        self.photo_base64 = book.get("photo") if book else None
        self.configure(bg=COLORS["card_bg"])

        setup_styles()

        main_frame = tk.Frame(self, bg=COLORS["card_bg"], padx=20, pady=20)
        main_frame.pack()

        tk.Label(main_frame, text=title, font=("Segoe UI", 14, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_primary"]).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        fields = ["titre", "auteur", "categorie", "annee_publication", "quantite_disponible", "statut"]
        self.entries = {}
        for i, field in enumerate(fields):
            tk.Label(main_frame, text=field.replace("_", " ").title() + ":", font=("Segoe UI", 10),
                     bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=i + 1, column=0, padx=5, pady=4, sticky="e")
            entry = ttk.Entry(main_frame, width=32)
            entry.grid(row=i + 1, column=1, padx=5, pady=4)
            self.entries[field] = entry

        if book:
            self.entries["titre"].insert(0, book.get("titre", ""))
            self.entries["auteur"].insert(0, book.get("auteur", ""))
            self.entries["categorie"].insert(0, book.get("categorie", ""))
            self.entries["annee_publication"].insert(0, str(book.get("annee_publication") or ""))
            self.entries["quantite_disponible"].insert(0, str(book.get("quantite_disponible", 0)))
            self.entries["statut"].insert(0, book.get("statut", "disponible"))

        photo_row = len(fields) + 1
        tk.Label(main_frame, text="Photo:", font=("Segoe UI", 10),
                 bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=photo_row, column=0, padx=5, pady=4, sticky="e")
        btn_frame = tk.Frame(main_frame, bg=COLORS["card_bg"])
        btn_frame.grid(row=photo_row, column=1, padx=5, pady=4, sticky="w")
        tk.Button(btn_frame, text="\U0001F4F7  Choose Photo", bg=COLORS["primary"], fg="white",
                  font=("Segoe UI", 9), border=0, padx=10, pady=4, cursor="hand2",
                  activebackground=COLORS["primary_hover"], activeforeground="white",
                  command=self._choose_photo).pack(side=tk.LEFT, padx=(0, 10))
        self.photo_preview = tk.Label(btn_frame, text="No photo selected", font=("Segoe UI", 8),
                                       bg=COLORS["input_bg"], fg=COLORS["text_muted"],
                                       relief=tk.SUNKEN, width=28, anchor="center", padx=5, pady=5)
        self.photo_preview.pack(side=tk.LEFT)

        if self.photo_base64:
            self._show_preview(self.photo_base64)

        action_row = photo_row + 1
        btn_frame2 = tk.Frame(main_frame, bg=COLORS["card_bg"])
        btn_frame2.grid(row=action_row, column=0, columnspan=2, pady=15)
        tk.Button(btn_frame2, text="  Save  ", bg=COLORS["primary"], fg="white",
                  font=("Segoe UI", 10, "bold"), padx=20, pady=6, border=0, cursor="hand2",
                  activebackground=COLORS["primary_hover"], activeforeground="white",
                  command=self._save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="  Cancel  ", bg=COLORS["card_bg"], fg=COLORS["text_secondary"],
                  font=("Segoe UI", 10), padx=20, pady=6, border=0, cursor="hand2",
                  relief=tk.SOLID, bd=1, highlightbackground=COLORS["border"],
                  activebackground=COLORS["danger_light"], activeforeground=COLORS["danger"],
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
        self.grab_set()
        self.wait_window()

    def _choose_photo(self):
        path = filedialog.askopenfilename(title="Select Book Cover", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")])
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
            img.thumbnail((100, 140), Image.LANCZOS)
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


CARD_W = 210
CARD_H = 340
COLS = 4
CARD_BG = "#ffffff"
CARD_SEL_BG = "#e3f2fd"
CARD_BORDER = "#e0e0e0"
CARD_SEL_BORDER = COLORS["primary"]


class BookCard(tk.Frame):
    def __init__(self, parent, book, on_click):
        super().__init__(parent, bg=CARD_BG, highlightbackground=CARD_BORDER, highlightthickness=1, width=CARD_W, height=CARD_H)
        self.book = book
        self.on_click = on_click
        self.selected = False
        self.pack_propagate(False)

        inner = tk.Frame(self, bg=CARD_BG, padx=6, pady=6)
        inner.pack(fill=tk.BOTH, expand=True)

        self.cover = tk.Label(inner, bg="#f0f0f0", text="\U0001F4D6", font=("Segoe UI", 28), anchor="center")
        self.cover.pack(fill=tk.X, pady=(0, 4))

        title = book.get("titre", "Unknown")
        author = book.get("auteur", "")
        year = book.get("annee_publication") or ""
        cat = book.get("categorie", "")
        qty = book.get("quantite_disponible", 0)

        tk.Label(inner, text=title, bg=CARD_BG, fg="#212121", font=("Segoe UI", 10, "bold"),
                 wraplength=180, anchor="w", justify="left").pack(fill=tk.X, pady=(0, 1))
        tk.Label(inner, text=author, bg=CARD_BG, fg="#616161", font=("Segoe UI", 9),
                 wraplength=180, anchor="w").pack(fill=tk.X)
        if year:
            tk.Label(inner, text=str(year), bg=CARD_BG, fg="#9e9e9e", font=("Segoe UI", 8),
                     anchor="w").pack(fill=tk.X)
        tk.Label(inner, text=cat, bg=CARD_BG, fg=COLORS["primary"], font=("Segoe UI", 8),
                 anchor="w").pack(fill=tk.X, pady=(1, 0))
        tk.Label(inner, text=f"\U0001F4E6 {qty} available", bg=CARD_BG,
                 fg="#388e3c" if qty > 0 else "#d32f2f",
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=tk.X)

        inner.bind("<Button-1>", self._click)
        for child in inner.winfo_children():
            child.bind("<Button-1>", self._click)
        self.bind("<Button-1>", self._click)

        self._load_cover()

    def _load_cover(self):
        photo_b64 = self.book.get("photo")
        if not photo_b64:
            return
        try:
            img_bytes = base64.b64decode(photo_b64)
            img = Image.open(io.BytesIO(img_bytes))
            img.thumbnail((CARD_W - 20, 160), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.cover.config(image=tk_img, text="")
            self.cover.image = tk_img
        except Exception:
            pass

    def _click(self, event=None):
        self.on_click(self.book)

    def set_selected(self, sel: bool):
        self.selected = sel
        self.config(highlightbackground=CARD_SEL_BORDER if sel else CARD_BORDER,
                    bg=CARD_SEL_BG if sel else CARD_BG)


class BooksView(tk.Frame):
    def __init__(self, parent, user_role="member"):
        super().__init__(parent)
        self.configure(bg=COLORS["bg"])
        self.pack(fill=tk.BOTH, expand=True)
        self.current_page = 1
        self.user_role = user_role
        self.selected_book = None
        self._card_refs = []

        toolbar = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))

        inner = tk.Frame(toolbar, bg=COLORS["card_bg"], padx=8, pady=8)
        inner.pack(fill=tk.X)

        def make_btn(text, cmd, bg=COLORS["primary"], fg="white", bold=False):
            btn = tk.Button(inner, text=text, bg=bg, fg=fg, font=("Segoe UI", 9, "bold" if bold else "normal"),
                           border=0, padx=12, pady=4, cursor="hand2", activebackground=bg, activeforeground=fg, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["primary_hover"] if bg == COLORS["primary"] else bg))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=bg))
            return btn

        make_btn("\u21bb Refresh", self._refresh)
        make_btn("\U0001F4CB Reserve", self._reserve_book, bg=COLORS["success"])

        if self.user_role == "admin":
            make_btn("+ Add Book", self._add_book)
            make_btn("\u270F Edit", self._edit_book, bg=COLORS["warning"], fg=COLORS["text_primary"])
            make_btn("\u2716 Delete", self._delete_book, bg=COLORS["danger"])

        tk.Label(inner, text="Search:", bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=(15, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(inner, width=16)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<Return>", lambda e: self._search())

        tk.Label(inner, text="Category:", bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=(10, 2))
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(inner, textvariable=self.cat_var, width=12)
        self.cat_combo.pack(side=tk.LEFT, padx=2)
        self._load_categories()

        tk.Label(inner, text="Status:", bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=(10, 2))
        self.status_var = tk.StringVar()
        ttk.Combobox(inner, textvariable=self.status_var, values=["", "disponible", "emprunt\u00e9", "r\u00e9serv\u00e9", "indisponible"], width=10).pack(side=tk.LEFT, padx=2)

        ttk.Button(inner, text="Filter", command=self._search).pack(side=tk.LEFT, padx=2)
        ttk.Button(inner, text="Clear", command=self._clear_filters).pack(side=tk.LEFT, padx=2)

        canvas_frame = tk.Frame(self, bg=COLORS["bg"])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["bg"], highlightthickness=0)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cards_container = tk.Frame(self.canvas, bg=COLORS["bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_container, anchor="nw", tags="inner")
        self.cards_container.bind("<Configure>", self._on_container_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        paginator = tk.Frame(self, bg=COLORS["bg"])
        paginator.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.page_label = tk.Label(paginator, text="Page 1", font=("Segoe UI", 9), bg=COLORS["bg"], fg=COLORS["text_secondary"])
        self.page_label.pack(side=tk.RIGHT, padx=5)
        ttk.Button(paginator, text="Next \u25B6", command=self._next_page).pack(side=tk.RIGHT, padx=2)
        ttk.Button(paginator, text="\u25C0 Prev", command=self._prev_page).pack(side=tk.RIGHT, padx=2)

        self._refresh()

    def _on_container_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _build_url(self):
        params = [("page", str(self.current_page)), ("per_page", "20")]
        if self.search_var.get().strip():
            params.append(("query", self.search_var.get().strip()))
        if self.cat_var.get():
            params.append(("categorie", self.cat_var.get()))
        if self.status_var.get():
            params.append(("statut", self.status_var.get()))
        return "/books/advanced?" + urllib.parse.urlencode(params)

    def _load_categories(self):
        status, data = api_client.get("/stats/")
        if status == 200:
            cats = list(data.get("categories", {}).keys())
            self.cat_combo["values"] = [""] + sorted(cats)

    def _on_card_click(self, book):
        self.selected_book = book
        for card in self._card_refs:
            card.set_selected(card.book.get("id_livre") == book.get("id_livre"))

    def _refresh(self):
        for w in self.cards_container.winfo_children():
            w.destroy()
        self._card_refs.clear()
        self.selected_book = None
        try:
            status, data = api_client.get(self._build_url())
            if status == 200:
                books = data.get("books", [])
                total = data.get("total", 0)
                page = data.get("page", 1)
                total_pages = data.get("total_pages", 1)
                for i, book in enumerate(books):
                    card = BookCard(self.cards_container, book, self._on_card_click)
                    card.grid(row=i // COLS, column=i % COLS, padx=4, pady=4)
                    self._card_refs.append(card)
                if not books:
                    tk.Label(self.cards_container, text="\U0001F50D No books found", font=("Segoe UI", 14),
                             bg=COLORS["bg"], fg=COLORS["text_muted"]).grid(row=0, column=0, padx=20, pady=40)
                self.page_label.config(text=f"Page {page} / {total_pages}  |  {total} books total")
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
        if not self.selected_book:
            messagebox.showinfo("Info", "Please select a book first.")
            return None
        return self.selected_book

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
        dialog = BookDialog(self, title="Add New Book")
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
