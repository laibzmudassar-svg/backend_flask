import sqlite3
import time

conn = sqlite3.connect('instance/app.db')
cur = conn.cursor()

cur.execute("SELECT title FROM posts LIMIT 1 OFFSET 250000;")
sample_title = cur.fetchone()[0]
print("Testing with title:", sample_title)

cur.execute("EXPLAIN QUERY PLAN SELECT * FROM posts WHERE title = ?;", (sample_title,))
for row in cur.fetchall(): print(row)

start = time.time()
cur.execute("SELECT * FROM posts WHERE title = ?;", (sample_title,))
results = cur.fetchall()
end = time.time()
print(f"Query took {(end-start)*1000:.2f} ms, found {len(results)} rows")