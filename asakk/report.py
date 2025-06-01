import psycopg2
import matplotlib.pyplot as plt
from data.config import DB_CONFIG
import logging
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('asakk.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.propagate = False


# --- СТАТИСТИЧЕСКИЙ АНАЛИЗ ---
def analyze_survey_data():
    """
    Анализ опроса: расчёт средних значений, дисперсий и выявление аномалий.
    Возвращает словарь:
        {
            'category': {
                'mean': среднее,
                'std': стандартное отклонение,
                'var': дисперсия,
                'anomalies': [список вопросов с аномальными оценками]
            },
            ...
        }
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.category, q.text, a.score
        FROM answers a
        JOIN questions q ON a.question_id = q.id
    ''')
    results = cursor.fetchall()
    conn.close()

    category_scores = defaultdict(list)
    question_scores = defaultdict(list)

    for category, question, score in results:
        category_scores[category].append(score)
        question_scores[(category, question)].append(score)

    analysis = {}

    for category, scores in category_scores.items():
        mean = np.mean(scores)
        std = np.std(scores)
        var = np.var(scores)

        anomalies = []

        for (cat, question), q_scores in question_scores.items():
            if cat == category:
                q_mean = np.mean(q_scores)
                if abs(q_mean - mean) > 2 * std:
                    anomalies.append({
                        'question': question,
                        'avg_score': round(q_mean, 2),
                        'deviation': round(abs(q_mean - mean), 2)
                    })

        analysis[category] = {
            'mean': round(mean, 2),
            'std': round(std, 2),
            'var': round(var, 2),
            'anomalies': anomalies
        }

    return analysis


# --- ОТЧЁТЫ СО СТАТИСТИКОЙ ---

def analyze_all_results():
    """Общий отчет по всем категориям с отклонениями"""
    survey_data = analyze_survey_data()
    if not survey_data:
        from tkinter import messagebox
        messagebox.showinfo("Нет данных", "Нет результатов для анализа")
        return None

    categories = list(survey_data.keys())
    means = [survey_data[c]['mean'] for c in categories]
    stds = [survey_data[c]['std'] for c in categories]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, means, yerr=stds, capsize=5, color='skyblue', edgecolor='black')
    ax.set_title("Средние оценки по категориям с отклонением")
    ax.set_xlabel("Категории")
    ax.set_ylabel("Средний балл")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    return fig


def calculate_category_trend(category):
    """
    Возвращает данные для построения тренда методом наименьших квадратов.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.score, a.timestamp
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE q.category = %s
        ORDER BY a.timestamp
    ''', (category,))
    results = cursor.fetchall()
    conn.close()

    if len(results) < 2:
        return None

    scores = [r[0] for r in results]
    X = np.arange(len(scores)).reshape(-1, 1)
    y = np.array(scores).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    trend_line = model.predict(X).flatten().tolist()

    return {
        "scores": scores,
        "trend": trend_line,
        "slope": model.coef_[0],
        "intercept": model.intercept_
    }


# --- ГРАФИЧЕСКИЕ ФУНКЦИИ ДЛЯ GUI ---

def analyze_category_data(category):
    """Возвращает данные по категории без построения графика"""
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
        return None

    questions, scores = zip(*results)
    max_length = 20
    short_questions = [q[:max_length] + '...' if len(q) > max_length else q for q in questions]

    return {
        "questions": short_questions,
        "scores": scores
    }


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
        return None

    scores, counts = zip(*results)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(scores, counts, color='skyblue')
    ax.set_title(f"Распределение оценок — {category}")
    ax.set_xlabel("Оценка (0–4)")
    ax.set_ylabel("Число ответов")
    ax.set_xticks(range(5))
    plt.tight_layout()

    return fig


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
        return None

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
    ax.set_title(f"Распределение оценок — {category}", fontsize=14)
    plt.tight_layout()

    return fig


# --- РЕКОМЕНДАЦИИ И ПРОГНОЗИРОВАНИЕ ---

def generate_recommendations():
    """Формирует рекомендации на основе слабых категорий"""
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


def predict_culture():
    """
    Прогнозирует изменение показателей культуры на основе последних 10 оценок.
    Возвращает словарь с прогнозом на следующий шаг (например, следующая оценка).
    """
    data = get_last_10_scores_per_category()
    predictions = {}

    for category, scores in data.items():
        if len(scores) < 2:
            continue  # Нужно минимум 2 точки для прогноза

        X = np.array(range(len(scores))).reshape(-1, 1)
        y = np.array(scores).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        next_point = np.array([[len(scores)]])  # Предсказываем следующую точку
        prediction = model.predict(next_point)[0][0]

        predicted_score = round(prediction, 1)
        last_score = round(scores[-1], 1)

        trend = "улучшение" if predicted_score > last_score else \
                "ухудшение" if predicted_score < last_score else "без изменений"

        predictions[category] = (
            f"Последняя оценка: {last_score}\n"
            f"Прогноз на следующий этап: {predicted_score}\n"
            f"Тренд: {trend}"
        )

    return predictions


def get_last_10_scores_per_category():
    """
    Забирает последние 10 оценок по каждой категории из базы данных.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """
        SELECT q.category, a.score, a.timestamp
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        ORDER BY q.category, a.timestamp DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    scores_by_category = defaultdict(list)
    for category, score, timestamp in rows:
        scores_by_category[category].append(score)

    # Оставляем только последние 10 записей для каждой категории
    for cat in scores_by_category:
        scores_by_category[cat] = scores_by_category[cat][:10]

    return scores_by_category


# --- ЭКСПОРТ И УПРАВЛЕНИЕ ДАННЫМИ ---

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
    try:
        # Добавляем вопрос
        cursor.execute(
            "INSERT INTO questions (text, category) VALUES (%s, %s) RETURNING id",
            (question_text, category)
        )
        question_id = cursor.fetchone()[0]

        # Добавляем рекомендацию с привязкой к вопросу
        cursor.execute(
            "INSERT INTO recommendations (category, event, question_id) VALUES (%s, %s, %s)",
            (category, event_text, question_id)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Ошибка при добавлении вопроса и мероприятия: {e}")
    finally:
        conn.close()

def delete_question_by_id(question_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM answers WHERE question_id = %s", (question_id,))
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Ошибка при удалении вопроса: {e}")
    finally:
        conn.close()


def delete_recommendation_by_category(category):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE category = %s", (category,))
    conn.commit()
    conn.close()

def build_category_bar_chart(data, category):
    """Строит график по данным категории"""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(data["questions"], data["scores"])
    ax.set_title(f"Оценки по категории: {category}")
    ax.set_xlabel("Вопросы")
    ax.set_ylabel("Оценка")
    plt.xticks(rotation=45, fontsize=8, ha='right')
    plt.tight_layout()
    return fig