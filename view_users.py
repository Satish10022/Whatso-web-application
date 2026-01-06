import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

print("📋 Users in users.db:")
for user in users:
    print(f"ID: {user[0]}, Phone: {user[1]}, Password: {user[2]}")

conn.close()
