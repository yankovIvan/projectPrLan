import csv
import os
from datetime import datetime
from collections import defaultdict

# Лимиты бюджетов по отделам
BUDGET_LIMITS = {
    "IT": 150000.0,
    "Marketing": 200000.0,
    "HR": 80000.0,
    "Operations": 120000.0
}

def process_expenses(input_file: str, output_dir: str = "reports"):
    """Автоматически агрегирует расходы, сверяет с лимитами и генерирует отчёт."""
    os.makedirs(output_dir, exist_ok=True)

    dept_totals = defaultdict(float)
    violations = []
    total_amount = 0.0
    records_count = 0

    try:
        with open(input_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dept = row["department"].strip()
                amount = float(row["amount"])
                records_count += 1
                total_amount += amount
                dept_totals[dept] += amount
    except FileNotFoundError:
        print(f" Ошибка: файл '{input_file}' не найден.")
        return
    except ValueError as e:
        print(f" Ошибка формата данных: {e}. Проверьте колонки amount/department.")
        return
    except Exception as e:
        print(f" Неожиданная ошибка: {e}")
        return

    # Сверка с бюджетом
    for dept, limit in BUDGET_LIMITS.items():
        spent = dept_totals.get(dept, 0.0)
        if spent > limit:
            violations.append(f" {dept}: превышение на {spent - limit:.2f} руб. (лимит: {limit:.2f})")

    # Генерация отчёта
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(output_dir, f"expense_report_{date_str}.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f" ОТЧЁТ ПО РАСХОДАМ | {date_str}\n")
        f.write("=" * 60 + "\n")
        f.write(f" Обработано записей: {records_count}\n")
        f.write(f" Общая сумма расходов: {total_amount:.2f} руб.\n\n")
        
        f.write(" Расходы по отделам:\n")
        for dept in sorted(dept_totals.keys()):
            spent = dept_totals[dept]
            limit = BUDGET_LIMITS.get(dept, "Не задан")
            status = " В норме" if isinstance(limit, (int, float)) and spent <= limit else \
                     " Превышение" if isinstance(limit, (int, float)) else "Без лимита"
            f.write(f"   • {dept}: {spent:.2f} руб. / лимит: {limit} руб. [{status}]\n")

        if violations:
            f.write(f"\n Нарушения бюджета:\n")
            for v in violations:
                f.write(f"   {v}\n")
        else:
            f.write("\n Все отделы в рамках утверждённого бюджета.\n")

    print(f" Отчёт сохранён: {report_path}")
    print(f" Итог: {total_amount:.2f} руб. | Отделов: {len(dept_totals)} | Нарушений: {len(violations)}")

if __name__ == "__main__":
    process_expenses("expenses.csv")
