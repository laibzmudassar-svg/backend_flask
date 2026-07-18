# Temporary fake database
users_db = {
    1: {"name": "Laiba", "email": "laiba@gmail.com"},
    2: {"name": "Mudassar", "email": "mudassar@gmail.com"}
}

def get_user_by_id(user_id):
    return users_db.get(user_id)

def add_user(user_id, name, email):
    users_db[user_id] = {"name": name, "email": email}
    return users_db[user_id] 