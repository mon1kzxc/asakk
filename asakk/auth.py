import psycopg2
from data.config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("asakk.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False  # ❌ Отключаем вывод в консоль


def get_all_users():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users ORDER BY role DESC")
    users = cursor.fetchall()
    conn.close()
    return users

def authenticate(username, ssh_key):
    logger.debug(f"Попытка входа: {username}")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username=%s AND ssh_key=%s", (username, ssh_key))
        user = cursor.fetchone()
        if user:
            logger.info(f"Пользователь вошёл: {user[1]} ({user[2]})")
        else:
            logger.warning("Неверный логин или SSH-ключ")
        return user
    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()


def add_user_to_db(username, ssh_key, role="Employee"):
    logger.debug(f"Добавление пользователя: {username}, роль: {role}")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, ssh_key, role) VALUES (%s, %s, %s)",
            (username, ssh_key, role)
        )
        conn.commit()
        logger.info(f"Пользователь {username} успешно добавлен")
    except Exception as e:
        logger.error(f"Не удалось добавить пользователя: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def delete_user_from_db(user_id):
    logger.debug(f"Удаление пользователя ID={user_id}")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            logger.warning(f"Пользователь с ID={user_id} не найден")
            return False

        cursor.execute("DELETE FROM answers WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s AND role != 'Admin'", (user_id,))
        conn.commit()
        logger.info(f"Пользователь ID={user_id} удален")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя: {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()