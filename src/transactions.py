import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import GOOGLE_CREDENTIALS_FILE, SHEET_URL, API_TOKEN

BASE_URL = "https://api.finolog.ru"
BIZ_ID = 17937  # ID бизнеса

def authorize_google_sheets():
    """
    Авторизация Google Sheets API.
    """
    print("Авторизация Google Sheets API...")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    print("Авторизация успешна!")
    return client

def fetch_all_transactions(biz_id, batch_size=200):
    """
    Получение всех транзакций из Финолога с пагинацией.
    """
    url = f"{BASE_URL}/v1/biz/{biz_id}/transaction"
    headers = {"Api-Token": API_TOKEN}

    all_transactions = []
    page = 1

    print("Получение транзакций из Финолога...")
    while True:
        params = {"page": page, "per_page": batch_size}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            transactions = response.json()

            if not transactions:
                break

            all_transactions.extend(transactions)
            print(f"Загружено {len(transactions)} транзакций с страницы {page}. Всего: {len(all_transactions)}")
            page += 1
        except requests.exceptions.RequestException as e:
            print("Ошибка при запросе транзакций:", e)
            break

    print(f"Всего загружено {len(all_transactions)} транзакций.")
    return all_transactions

def update_google_sheet(sheet_name, transactions):
    """
    Полностью перезаписывает Google Таблицу всеми транзакциями из Финолога.
    """
    print("Подключение к Google Таблице...")
    client = authorize_google_sheets()
    sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)

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

    # Устанавливаем формат "Дата" для нужных столбцов
    set_date_format(sheet_name, column_letter="B")  # Столбец "Дата"
    set_date_format(sheet_name, column_letter="K")  # Столбец "Создано"
    set_date_format(sheet_name, column_letter="L")  # Столбец "Обновлено"

    print("Таблица успешно обновлена!")

def set_date_format(sheet_name, column_letter):
    """
    Устанавливает формат "Дата" для указанного столбца в Google Таблице.
    """
    client = authorize_google_sheets()
    spreadsheet = client.open_by_url(SHEET_URL)
    sheet = spreadsheet.worksheet(sheet_name)
    sheet_id = sheet.id  # Получаем ID листа

    # Определяем индекс столбца
    column_index = ord(column_letter.upper()) - ord('A')  # A=0, B=1, ...

    # Формируем запрос для установки формата
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": column_index,
                    "endColumnIndex": column_index + 1,
                    "startRowIndex": 1  # С 1 строки, чтобы не затрагивать заголовки
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "DATE",
                            "pattern": "yyyy-mm-dd"  # Формат даты
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        }
    ]

    # Выполняем batchUpdate через объект Spreadsheet
    body = {"requests": requests}
    spreadsheet.batch_update(body)
    print(f"Формат 'Дата' установлен для столбца {column_letter}.")