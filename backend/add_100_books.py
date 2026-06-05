import sys; sys.path.insert(0, '.')
import ssl, urllib.request, urllib.parse, json, time
from app.database import SessionLocal
from app.models.book import Book

ssl_ctx = ssl._create_unverified_context()

BOOKS = [
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937),
    ("Fahrenheit 451", "Ray Bradbury", "Science Fiction", 1953),
    ("Jane Eyre", "Charlotte Bronte", "Romance", 1847),
    ("Animal Farm", "George Orwell", "Fiction", 1945),
    ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy", 1954),
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy", 1997),
    ("The Da Vinci Code", "Dan Brown", "Thriller", 2003),
    ("The Alchemist", "Paulo Coelho", "Fiction", 1988),
    ("Brave New World", "Aldous Huxley", "Science Fiction", 1932),
    ("Wuthering Heights", "Emily Bronte", "Romance", 1847),
    ("The Road", "Cormac McCarthy", "Fiction", 2006),
    ("The Hunger Games", "Suzanne Collins", "Young Adult", 2008),
    ("The Martian", "Andy Weir", "Science Fiction", 2011),
    ("Gone Girl", "Gillian Flynn", "Thriller", 2012),
    ("The Girl on the Train", "Paula Hawkins", "Thriller", 2015),
    ("The Notebook", "Nicholas Sparks", "Romance", 1996),
    ("Dune", "Frank Herbert", "Science Fiction", 1965),
    ("The Shining", "Stephen King", "Horror", 1977),
    ("It", "Stephen King", "Horror", 1986),
    ("Dracula", "Bram Stoker", "Horror", 1897),
    ("Frankenstein", "Mary Shelley", "Horror", 1818),
    ("The Picture of Dorian Gray", "Oscar Wilde", "Fiction", 1890),
    ("Moby-Dick", "Herman Melville", "Fiction", 1851),
    ("War and Peace", "Leo Tolstoy", "Fiction", 1869),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Fiction", 1866),
    ("The Adventures of Huckleberry Finn", "Mark Twain", "Fiction", 1884),
    ("Great Expectations", "Charles Dickens", "Fiction", 1861),
    ("A Tale of Two Cities", "Charles Dickens", "Fiction", 1859),
    ("The Odyssey", "Homer", "Classic", -800),
    ("The Iliad", "Homer", "Classic", -750),
    ("Les Miserables", "Victor Hugo", "Fiction", 1862),
    ("The Count of Monte Cristo", "Alexandre Dumas", "Fiction", 1844),
    ("The Three Musketeers", "Alexandre Dumas", "Fiction", 1844),
    ("Don Quixote", "Miguel de Cervantes", "Fiction", 1605),
    ("The Divine Comedy", "Dante Alighieri", "Classic", 1320),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction", 1967),
    ("Love in the Time of Cholera", "Gabriel Garcia Marquez", "Romance", 1985),
    ("The Kite Runner", "Khaled Hosseini", "Fiction", 2003),
    ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction", 2007),
    ("Life of Pi", "Yann Martel", "Fiction", 2001),
    ("The Book Thief", "Markus Zusak", "Fiction", 2005),
    ("The Fault in Our Stars", "John Green", "Young Adult", 2012),
    ("Looking for Alaska", "John Green", "Young Adult", 2005),
    ("The Maze Runner", "James Dashner", "Young Adult", 2009),
    ("Divergent", "Veronica Roth", "Young Adult", 2011),
    ("Twilight", "Stephenie Meyer", "Romance", 2005),
    ("Eragon", "Christopher Paolini", "Fantasy", 2002),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy", 2007),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy", 1996),
    ("The Witcher", "Andrzej Sapkowski", "Fantasy", 1993),
    ("American Gods", "Neil Gaiman", "Fantasy", 2001),
    ("Good Omens", "Neil Gaiman", "Fantasy", 1990),
    ("The Handmaid's Tale", "Margaret Atwood", "Science Fiction", 1985),
    ("Neuromancer", "William Gibson", "Science Fiction", 1984),
    ("Ender's Game", "Orson Scott Card", "Science Fiction", 1985),
    ("Foundation", "Isaac Asimov", "Science Fiction", 1951),
    ("I, Robot", "Isaac Asimov", "Science Fiction", 1950),
    ("The Time Machine", "H.G. Wells", "Science Fiction", 1895),
    ("The War of the Worlds", "H.G. Wells", "Science Fiction", 1898),
    ("Slaughterhouse-Five", "Kurt Vonnegut", "Fiction", 1969),
    ("Catch-22", "Joseph Heller", "Fiction", 1961),
    ("The Bell Jar", "Sylvia Plath", "Fiction", 1963),
    ("On the Road", "Jack Kerouac", "Fiction", 1957),
    ("Lolita", "Vladimir Nabokov", "Fiction", 1955),
    ("The Stranger", "Albert Camus", "Fiction", 1942),
    ("The Metamorphosis", "Franz Kafka", "Fiction", 1915),
    ("The Trial", "Franz Kafka", "Fiction", 1925),
    ("Ulysses", "James Joyce", "Fiction", 1922),
    ("Mrs Dalloway", "Virginia Woolf", "Fiction", 1925),
    ("To the Lighthouse", "Virginia Woolf", "Fiction", 1927),
    ("The Great Alone", "Kristin Hannah", "Fiction", 2018),
    ("The Nightingale", "Kristin Hannah", "Fiction", 2015),
    ("Where the Crawdads Sing", "Delia Owens", "Fiction", 2018),
    ("Educated", "Tara Westover", "Non-Fiction", 2018),
    ("Sapiens", "Yuval Noah Harari", "Non-Fiction", 2011),
    ("Atomic Habits", "James Clear", "Non-Fiction", 2018),
    ("The Art of War", "Sun Tzu", "Non-Fiction", -500),
    ("Thinking Fast and Slow", "Daniel Kahneman", "Non-Fiction", 2011),
    ("A Brief History of Time", "Stephen Hawking", "Science", 1988),
    ("The Selfish Gene", "Richard Dawkins", "Science", 1976),
    ("Cosmos", "Carl Sagan", "Science", 1980),
    ("The Origin of Species", "Charles Darwin", "Science", 1859),
    ("The God Delusion", "Richard Dawkins", "Non-Fiction", 2006),
    ("Outliers", "Malcolm Gladwell", "Non-Fiction", 2008),
    ("Freakonomics", "Steven Levitt", "Non-Fiction", 2005),
    ("The Tipping Point", "Malcolm Gladwell", "Non-Fiction", 2000),
    ("Steve Jobs", "Walter Isaacson", "Biography", 2011),
    ("Einstein", "Walter Isaacson", "Biography", 2007),
    ("The Diary of a Young Girl", "Anne Frank", "Biography", 1947),
    ("Long Walk to Freedom", "Nelson Mandela", "Biography", 1994),
    ("Becoming", "Michelle Obama", "Biography", 2018),
    ("The Silent Patient", "Alex Michaelides", "Thriller", 2019),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Thriller", 2005),
    ("All the Light We Cannot See", "Anthony Doerr", "Fiction", 2014),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "Science Fiction", 1979),
    ("Gone with the Wind", "Margaret Mitchell", "Fiction", 1936),
    ("The Little Prince", "Antoine de Saint-Exupery", "Fiction", 1943),
]

def fetch_cover(book_title):
    try:
        search_url = "https://openlibrary.org/search.json?q=" + urllib.parse.quote(book_title) + "&limit=1"
        with urllib.request.urlopen(search_url, timeout=15, context=ssl_ctx) as r:
            data = json.loads(r.read())
        docs = data.get("docs", [])
        if docs and docs[0].get("cover_i"):
            img_url = "https://covers.openlibrary.org/b/id/" + str(docs[0]["cover_i"]) + "-L.jpg"
            with urllib.request.urlopen(img_url, timeout=15, context=ssl_ctx) as ir:
                return ir.read()
    except:
        pass
    return None

db = SessionLocal()
try:
    added = 0
    for i, (titre, auteur, cat, annee) in enumerate(BOOKS, 1):
        cover_data = fetch_cover(titre)
        book = Book(
            titre=titre,
            auteur=auteur,
            categorie=cat,
            annee_publication=annee if annee > 0 else None,
            quantite_disponible=3,
            statut="disponible",
            photo=cover_data
        )
        db.add(book)
        status = "YES" if cover_data else "NO"
        print(f"[{i}/100] Added: {titre} (cover: {status})")
        added += 1
        if i % 10 == 0:
            db.commit()
            print(f"  --- checkpoint: {i} books committed ---")
            time.sleep(0.5)
    db.commit()
    print(f"\nDone! {added} books added successfully.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
