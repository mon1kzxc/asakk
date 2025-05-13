from .config import DB_CONFIG
from asakk.database import get_connection

def check_connection():
    try:
        conn = get_connection()
        print("Подключение к базе данных успешно!")
        conn.close()
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")

if __name__ == "__main__":
    check_connection()