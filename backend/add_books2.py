import sys; sys.path.insert(0, '.')
import ssl, urllib.request, urllib.parse, json
from app.database import SessionLocal
from app.models.book import Book

ssl_ctx = ssl._create_unverified_context()

BOOKS = [
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 1925),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", 1960),
    ("1984", "George Orwell", "Science Fiction", 1949),
    ("Pride and Prejudice", "Jane Austen", "Romance", 1813),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction", 1951),
]

db = SessionLocal()
try:
    for titre, auteur, cat, annee in BOOKS:
        search_url = "https://openlibrary.org/search.json?q=" + urllib.parse.quote(titre) + "&limit=1"
        with urllib.request.urlopen(search_url, timeout=10, context=ssl_ctx) as r:
            data = json.loads(r.read())
        docs = data.get("docs", [])
        cover_data = None
        if docs and docs[0].get("cover_i"):
            img_url = "https://covers.openlibrary.org/b/id/" + str(docs[0]["cover_i"]) + "-L.jpg"
            try:
                with urllib.request.urlopen(img_url, timeout=10, context=ssl_ctx) as ir:
                    cover_data = ir.read()
            except:
                pass
        book = Book(titre=titre, auteur=auteur, categorie=cat, annee_publication=annee, quantite_disponible=3, statut="disponible", photo=cover_data)
        db.add(book)
        status = "YES" if cover_data else "NO"
        print(f"Added: {titre} (cover: {status})")
    db.commit()
    print("Done!")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
