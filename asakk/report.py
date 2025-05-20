import psycopg2
import matplotlib.pyplot as plt
from data.config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('asakk.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.propagate = False

def analyze_all_results():
    """Общий отчет по всем категориям"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.category, AVG(a.score) AS avg_score
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        GROUP BY q.category
    ''')
    results = cursor.fetchall()
    conn.close()

    if results:
        categories, scores = zip(*results)
        plt.bar(categories, scores)
        plt.title("Средние оценки по категориям")
        plt.xlabel("Категории")
        plt.ylabel("Средний балл")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        from tkinter import messagebox
        messagebox.showinfo("Нет данных", "Еще нет результатов для анализа")


def analyze_category(category):
    """Отчет по одной категории с укороченными подписями"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.text, a.score
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE q.category = %s
    ''', (category,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        from tkinter import messagebox
        messagebox.showinfo("Нет данных", f"Нет результатов для категории '{category}'")
        return

    questions, scores = zip(*results)

    max_length = 20
    short_questions = [q[:max_length] + '...' if len(q) > max_length else q for q in questions]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(short_questions, scores)
    plt.title(f"Оценки по категории: {category}")
    plt.xlabel("Вопросы")
    plt.ylabel("Оценка")

    plt.xticks(rotation=45, fontsize=8, ha='right')

    plt.tight_layout()

    plt.show()


def score_distribution_by_category(category):
    """Гистограмма распределения оценок по категории"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.score, COUNT(*) AS count
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE q.category = %s
        GROUP BY a.score
    ''', (category,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        from tkinter import messagebox
        messagebox.showinfo("Нет данных", f"Нет результатов для категории '{category}'")
        return

    scores, counts = zip(*results)

    plt.bar(scores, counts, color='skyblue')
    plt.title(f"Распределение оценок — {category}")
    plt.xlabel("Оценка (0–4)")
    plt.ylabel("Число ответов")
    plt.xticks(range(5))
    plt.tight_layout()
    plt.show()



def pie_chart_by_category(category):
    """Круговая диаграмма оценок по категории"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.score, COUNT(*) AS count
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE q.category = %s
        GROUP BY a.score
    ''', (category,))
    results = cursor.fetchall()
    conn.close()

    if not results:
        from tkinter import messagebox
        messagebox.showinfo("Нет данных", f"Нет результатов для категории '{category}'")
        return

    score_counts = dict(results)
    labels = []
    sizes = []

    for i in range(5):
        labels.append(f"{i} баллов")
        sizes.append(score_counts.get(i, 0))

    filtered_labels = [labels[i] if sizes[i] > 0 else '' for i in range(len(labels))]
    explode = [0.05 if size > 0 else 0 for size in sizes]
    
    fig, ax = plt.subplots()
    ax.pie(
        sizes,
        labels=filtered_labels,
        autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
        startangle=90,
        colors=['#ff6b6b', '#ff9f43', '#ffd93d', '#61a5e8', '#7cd992'],
        explode=explode,
        textprops={'fontsize': 10}
    )
    ax.axis('equal')  
    plt.title(f"Распределение оценок — {category}", fontsize=14)
    plt.tight_layout()
    plt.show()


def generate_recommendations():
    """Формирует рекомендации на основе слабых категорий"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.category, AVG(a.score) AS avg_score
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        GROUP BY q.category
    ''')
    results = cursor.fetchall()
    conn.close()

    low_categories = [cat for cat, score in results if score < 2]
    if not low_categories:
        return {}

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, event FROM recommendations
        WHERE category = ANY(%s)
    ''', (low_categories,))
    events = cursor.fetchall()
    conn.close()

    recommendations = {}
    for cat in low_categories:
        recommendations[cat] = []

    for cat, event in events:
        if cat in recommendations:
            recommendations[cat].append(event)

    return recommendations


def export_to_csv(filename="results.csv"):
    """Экспорт всех данных в CSV-файл"""
    import csv
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, q.text, q.category, a.score
        FROM answers a
        JOIN users u ON a.user_id = u.id
        JOIN questions q ON a.question_id = q.id
    ''')
    data = cursor.fetchall()
    conn.close()

    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Пользователь", "Вопрос", "Категория", "Оценка"])
        writer.writerows(data)


def generate_recommendations():
    """
    Формирует рекомендации на основе слабых категорий (оценка < 2)
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Средние оценки по категориям
    cursor.execute('''
        SELECT q.category, AVG(a.score) AS avg_score
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        GROUP BY q.category
    ''')
    results = cursor.fetchall()
    conn.close()

    low_categories = [cat for cat, score in results if score < 2]
    if not low_categories:
        return {}

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Загружаем мероприятия по слабым категориям
    cursor.execute('''
        SELECT category, event FROM recommendations
        WHERE category = ANY(%s)
    ''', (low_categories,))
    events = cursor.fetchall()
    conn.close()

    # Группируем мероприятия по категориям
    recommendations = {}
    for cat in low_categories:
        recommendations[cat] = []

    for cat, event in events:
        if cat in recommendations:
            recommendations[cat].append(event)

    return recommendations


def save_answers(user_id, answers):
    """
    Сохраняет ответы пользователя в БД
    :param user_id: ID пользователя
    :param answers: словарь {question_id: score}
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    for question_id, score in answers.items():
        cursor.execute(
            "INSERT INTO answers (user_id, question_id, score) VALUES (%s, %s, %s)",
            (user_id, question_id, score)
        )
    
    conn.commit()
    conn.close()

def next_question(self):
    selected = self.var.get()
    if selected == -1:
        messagebox.showwarning("Ошибка", "Выберите оценку.")
        return

    q_id = self.questions[self.current_index][0]
    self.answers[q_id] = selected
    self.current_index += 1

    if self.current_index < len(self.questions):
        self.question_label.config(text=self.get_current_question_text())
        self.var.set(-1)
    else:
        from asakk.report import save_answers
        save_answers(self.user[0], self.answers)
        messagebox.showinfo("Готово", "Ответы сохранены!")
        self.root.quit()

def add_recommendation_to_db(category, event):
    logger.debug(f"Добавление мероприятия: {event} → {category}")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recommendations (category, event) VALUES (%s, %s)",
            (category, event)
        )
        conn.commit()
        logger.info(f"Мероприятие '{event}' добавлено в '{category}'")
    except Exception as e:
        logger.error(f"Не удалось добавить мероприятие: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_categ_to_adm():
    return [
        "Ценности",
        "Коммуникации",
        "Лидерство",
        "Инновации",
        "Работа в команде",
        "Работа и личная жизнь"
    ]


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


def delete_question_by_id(question_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM answers WHERE question_id = %s", (question_id,))
    cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
    conn.commit()
    conn.close()


def delete_recommendation_by_category(category):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE category = %s", (category,))
    conn.commit()
    conn.close()