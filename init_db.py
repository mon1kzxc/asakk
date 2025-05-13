import psycopg2
from data.config import DB_CONFIG

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Employee', 'Manager', 'Admin')),
            ssh_key TEXT NOT NULL
        )
    ''')

    # Таблица вопросов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # НОВАЯ ТАБЛИЦА: Рекомендации по улучшению культуры
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            event TEXT NOT NULL
        )
    ''')

    # Вставьте тестовые данные (если нужно)
    conn.commit()
    conn.close()
    print("✅ База данных и таблицы созданы.")

if __name__ == '__main__':
    init_db()