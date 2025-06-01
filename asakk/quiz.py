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

def get_categories():
    logger.debug("Запрос категорий из БД")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM questions")
        categories = [row[0] for row in cursor.fetchall()]
        logger.info(f"Категории загружены: {categories}")
        return categories
    except Exception as e:
        logger.error(f"Не удалось загрузить категории: {e}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

def get_questions_by_category(category=None):
    """
    Возвращает все вопросы из указанной категории.
    Если category == 'Все категории', возвращаются все вопросы
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    if category == "Все категории":
        cursor.execute("SELECT id, text, category FROM questions")
    else:
        cursor.execute("SELECT id, text, category FROM questions WHERE category=%s", (category,))
    
    questions = cursor.fetchall()
    conn.close()
    return questions

def save_answers(user_id, answers):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    for q_id, score in answers.items():
        cursor.execute(
            "INSERT INTO answers (user_id, question_id, score) VALUES (%s, %s, %s)",
            (user_id, q_id, score)
        )

def add_question_with_recommendation(category, question_text, event_text):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Добавляем вопрос
    cursor.execute(
        "INSERT INTO questions (text, category) VALUES (%s, %s) RETURNING id",
        (question_text, category)
    )
    question_id = cursor.fetchone()[0]

    # Добавляем связанную рекомендацию
    cursor.execute(
        "INSERT INTO recommendations (category, event) VALUES (%s, %s)",
        (category, event_text)
    )

    conn.commit()
    conn.close()


def add_question_to_db(text, category):
    logger.debug(f"Добавление вопроса: '{text}' → {category}")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO questions (text, category) VALUES (%s, %s) RETURNING id",
            (text, category)
        )
        question_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Вопрос '{text}' добавлен (ID={question_id})")
        return question_id
    except Exception as e:
        logger.error(f"Не удалось добавить вопрос: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_questions_by_categories(categories):
    """
    Возвращает вопросы из указанных категорий.
    categories - список названий категорий.
    """
    if not categories:
        return []

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Используем SQL IN для выбора вопросов из нескольких категорий
    placeholders = ', '.join(['%s'] * len(categories))
    query = f"SELECT id, text, category FROM questions WHERE category IN ({placeholders})"
    
    cursor.execute(query, categories)
    questions = cursor.fetchall()
    
    conn.close()
    return questions