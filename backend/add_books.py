import sys; sys.path.insert(0, '.')
import urllib.request, urllib.parse, json
from app.database import SessionLocal
from app.models.book import Book

BOOKS = [
    {"titre": "The Great Gatsby", "auteur": "F. Scott Fitzgerald", "categorie": "Fiction", "annee": 1925},
    {"titre": "To Kill a Mockingbird", "auteur": "Harper Lee", "categorie": "Fiction", "annee": 1960},
    {"titre": "1984", "auteur": "George Orwell", "categorie": "Science Fiction", "annee": 1949},
    {"titre": "Pride and Prejudice", "auteur": "Jane Austen", "categorie": "Romance", "annee": 1813},
    {"titre": "The Catcher in the Rye", "auteur": "J.D. Salinger", "categorie": "Fiction", "annee": 1951},
]

def fetch_cover(book_title):
    try:
        search_url = "https://openlibrary.org/search.json?q=" + urllib.parse.quote(book_title) + "&limit=1"
        with urllib.request.urlopen(search_url, timeout=10) as r:
            data = json.loads(r.read())
        docs = data.get("docs", [])
        if docs and docs[0].get("cover_i"):
            cover_id = docs[0]["cover_i"]
            img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            with urllib.request.urlopen(img_url, timeout=10) as ir:
                return ir.read()
    except Exception as e:
        print(f"  Cover fetch error: {e}")
    return None

db = SessionLocal()
try:
    for b in BOOKS:
        cover_data = fetch_cover(b["titre"])
        book = Book(
            titre=b["titre"],
            auteur=b["auteur"],
            categorie=b["categorie"],
            annee_publication=b["annee"],
            quantite_disponible=3,
            statut="disponible",
            photo=cover_data
        )
        db.add(book)
        print(f'Added: {b["titre"]} (cover: {"YES" if cover_data else "NO"})')
    db.commit()
    print("Done! 5 books added successfully.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
