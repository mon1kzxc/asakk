import csv

def export_to_csv(data, filename="results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Категория", "Средняя оценка"])
        writer.writerows(data)