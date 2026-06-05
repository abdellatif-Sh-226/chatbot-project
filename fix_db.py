import pymysql
conn = pymysql.connect(host='localhost', user='root', password='', database='library_chatbot')
with conn.cursor() as cur:
    for stmt in [
        "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'member'",
        "CREATE TABLE IF NOT EXISTS reservations (id INTEGER AUTO_INCREMENT PRIMARY KEY, user_id INTEGER NOT NULL, book_id INTEGER NOT NULL, status VARCHAR(20) DEFAULT 'pending', created_at DATETIME)",
    ]:
        try:
            cur.execute(stmt)
            print(f'OK: {stmt[:50]}...')
        except Exception as e:
            print(f'ERR: {e}')
    conn.commit()
    cur.execute("DESCRIBE users")
    for r in cur.fetchall():
        print(r)
print('DONE')
