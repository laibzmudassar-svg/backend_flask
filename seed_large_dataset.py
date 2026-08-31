import sqlite3
import random
import time

conn = sqlite3.connect('instance/app.db')
cur = conn.cursor()

# Speed up bulk insert
cur.execute("PRAGMA journal_mode = WAL;")
cur.execute("PRAGMA synchronous = OFF;")

titles = ["Post about Python", "Post about Flask", "Post about SQL",
          "Post about Indexing", "Post about Performance", "Random Update",
          "Weekly Digest", "Announcement", "Tips and Tricks", "Deep Dive"]

# Make sure we have enough users to assign posts to
cur.execute("SELECT id FROM users;")
user_ids = [row[0] for row in cur.fetchall()]
if not user_ids:
    print("No users found — create at least one user first!")
    exit()

print(f"Seeding 500,000 posts using {len(user_ids)} existing users...")
start = time.time()

batch = []
for i in range(500000):
    batch.append((
        random.choice(user_ids),
        f"{random.choice(titles)} #{i}",
        f"Content for post {i}"
    ))
    if len(batch) == 5000:
        cur.executemany("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", batch)
        batch = []

if batch:
    cur.executemany("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", batch)

conn.commit()
end = time.time()
print(f"Done! Inserted 500,000 rows in {end - start:.2f} seconds.")

cur.execute("SELECT COUNT(*) FROM posts;")
print("Total posts now:", cur.fetchone())
conn.close()