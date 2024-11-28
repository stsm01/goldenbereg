import datetime
from transactions import authorize_google_sheets, fetch_all_transactions
from src.config import SHEET_URL


# Параметры
SHEET_NAME = "Transactions"  # Имя листа в Google Таблице
BIZ_ID = 17937  # ID бизнеса в Финологе


def update_google_sheet(transactions):
    """
    Полностью перезаписывает Google Таблицу всеми транзакциями из Финолога.
    """
    print("Подключение к Google Таблице...")
    client = authorize_google_sheets()
    sheet = client.open_by_url(SHEET_URL).worksheet(SHEET_NAME)

    print("Очищаем старые данные...")
    headers = [
        "ID", "Дата", "Бизнес ID", "Счёт ID", "Тип", "Категория ID",
        "Контрагент ID", "Описание", "Сумма", "Статус", "Создано", "Обновлено"
    ]
    sheet.clear()
    sheet.append_row(headers, value_input_option="USER_ENTERED")  # Записываем заголовки

    print(f"Добавляем {len(transactions)} транзакций...")
    formatted_transactions = [
        [
            tx.get("id"),
            tx.get("date"),
            tx.get("biz_id"),
            tx.get("account_id"),
            tx.get("type"),
            tx.get("category_id"),
            tx.get("contractor_id"),
            tx.get("description"),
            tx.get("value"),
            tx.get("status"),
            tx.get("created_at"),
            tx.get("updated_at")
        ]
        for tx in transactions
    ]
    sheet.append_rows(formatted_transactions, value_input_option="USER_ENTERED")
    print("Таблица успешно обновлена!")


def main():
    """
    Основная функция для полной перезаписи Google Таблицы.
    """
    try:
        print("Запуск обновления...")
        # Получаем данные из Финолога
        transactions = fetch_all_transactions(BIZ_ID)

        if not transactions:
            print("Нет данных для обновления.")
            return

        # Перезаписываем Google Таблицу
        update_google_sheet(transactions)

        print("Обновление завершено успешно!")
    except Exception as e:
        print("Ошибка в процессе обновления:", e)


if __name__ == "__main__":
    main()