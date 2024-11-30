import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import GOOGLE_CREDENTIALS_FILE, SHEET_URL, API_TOKEN

BASE_URL = "https://api.finolog.ru"

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

def fetch_groups(biz_id):
    """
    Получение всех групп из Финолога.
    """
    url = f"{BASE_URL}/v1/biz/{biz_id}/group"
    headers = {
        "Api-Token": API_TOKEN
    }

    try:
        print("Получение групп из Финолога...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        groups = response.json()
        print(f"Получено {len(groups)} групп.")
        return groups
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе групп:", e)
        return []

def format_group(group):
    """
    Форматирует объект группы для записи в Google Таблицу.
    """
    return [
        group.get("id"),
        group.get("biz_id"),
        group.get("name"),
        group.get("model_type"),
        group.get("type"),
        group.get("created_by_id"),
        group.get("updated_by_id"),
        group.get("created_at"),
        group.get("updated_at"),
        group.get("parent_id"),
        group.get("deleted_at"),
    ]

def add_groups_to_sheet(groups, sheet_name="Groups"):
    """
    Добавляет группы в Google Таблицу.
    """
    client = authorize_google_sheets()
    sheet = client.open_by_url(SHEET_URL)

    try:
        worksheet = sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Лист '{sheet_name}' не найден. Создаём новый лист...")
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    # Заголовки таблицы
    headers = [
        "ID группы",       # group.get("id")
        "ID бизнеса",      # group.get("biz_id")
        "Название группы", # group.get("name")
        "Модель",          # group.get("model_type")
        "Тип",             # group.get("type")
        "Создано кем",     # group.get("created_by_id")
        "Обновлено кем",   # group.get("updated_by_id")
        "Дата создания",   # group.get("created_at")
        "Дата обновления", # group.get("updated_at")
        "ID родителя",     # group.get("parent_id")
        "Удалено",         # group.get("deleted_at")
    ]

    # Очищаем данные и добавляем заголовки
    print("Очищаем старые данные...")
    worksheet.clear()
    worksheet.append_row(headers, value_input_option="USER_ENTERED")

    # Форматируем группы для записи
    rows = [format_group(group) for group in groups]
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"Добавлено {len(rows)} групп в '{sheet_name}'.")

if __name__ == "__main__":
    BIZ_ID = 17937
    groups = fetch_groups(BIZ_ID)
    if groups:
        add_groups_to_sheet(groups)
    else:
        print("Нет групп для добавления.")