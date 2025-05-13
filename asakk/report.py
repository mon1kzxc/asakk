import psycopg2
from data.config import DB_CONFIG
import matplotlib.pyplot as plt

def analyze_all_results():
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