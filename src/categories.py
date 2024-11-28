import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import GOOGLE_CREDENTIALS_FILE, SHEET_URL, API_TOKEN

BASE_URL = "https://api.finolog.ru"

def authorize_google_sheets():
    print("Авторизация Google Sheets API...")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        print("Авторизация успешна!")
        return client
    except Exception as e:
        print("Ошибка при авторизации:", e)
        return None

def fetch_categories(biz_id, limit=3):
    url = f"{BASE_URL}/v1/biz/{biz_id}/category"
    headers = {
        "Api-Token": API_TOKEN
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем статус ответа
        categories = response.json()  # Преобразуем ответ в JSON
        print(f"Получено {len(categories)} категорий.")
        return categories
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе категорий:", e)
        return []

def format_category(category):
    """
    Формирует список для таблицы из объекта категории.
    """
    return [
        category.get("id"),
        category.get("biz_id"),
        category.get("type"),
        category.get("code"),
        category.get("name"),
        category.get("created_at"),
        category.get("updated_at"),
        category.get("created_by_id"),
        category.get("updated_by_id"),
        category.get("activities"),
        category.get("cash_in_out"),
        category.get("color"),
        category.get("description"),
        category.get("tax_type"),
        category.get("group_id"),
        category.get("interest_repayment")
    ]

def add_categories_to_sheet(categories, sheet_name="Categories"):
    client = authorize_google_sheets()
    if client is None:
        print("Не удалось авторизоваться. Операция прервана.")
        return

    sheet = client.open_by_url(SHEET_URL)

    try:
        # Попытка открыть лист
        worksheet = sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # Создаём лист, если его нет
        print(f"Лист '{sheet_name}' не найден. Создаём новый лист...")
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    # Заголовки таблицы
    headers = [
        "ID",
        "Бизнес ID",
        "Тип",
        "Код",
        "Название",
        "Дата создания",
        "Дата обновления",
        "Создано пользователем",
        "Обновлено пользователем",
        "Активность",
        "Наличные",
        "Цвет",
        "Описание",
        "Тип налогообложения",
        "Группа ID",
        "Погашение процентов"
    ]

    # Проверяем, есть ли заголовки
    if not worksheet.row_values(1):
        print("Добавляем заголовки в таблицу...")
        worksheet.append_row(headers)

    # Собираем все существующие ID из таблицы
    existing_ids = set(row[0] for row in worksheet.get_all_values()[1:] if row)
    # Фильтруем транзакции, оставляя только новые
    new_categories = [tx for tx in categories if str(tx.get("id")) not in existing_ids]

    if not new_categories:
        print("Нет новых категорий для добавления.")
        return
    rows = [format_category(tx) for tx in new_categories]
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")

    print(f"Добавлено {len(rows)} новых категорий.")

if __name__ == "__main__":
    biz_id = 17937
    categories = fetch_categories(biz_id)
    add_categories_to_sheet(categories)