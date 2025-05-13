import psycopg2
from data.config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Подключение к БД успешно!")
    conn.close()
except Exception as e:
    print("❌ Ошибка подключения:", e)