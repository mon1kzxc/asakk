import psycopg2
from data.config import DB_CONFIG

def get_categories():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

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