import psycopg2
from data.config import DB_CONFIG

def authenticate(username, ssh_key):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND ssh_key=%s", (username, ssh_key))
    user = cursor.fetchone()
    conn.close()
    return user