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

def fetch_accounts(biz_id):
    url = f"{BASE_URL}/v1/biz/{biz_id}/account"
    headers = {
        "Api-Token": API_TOKEN
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        accounts = response.json() or []
        print(f"Получено {len(accounts)} счетов.")
        return accounts
    except requests.exceptions.RequestException as e:
        print("Ошибка при запросе счетов:", e)
        return []

def format_account(account):
    return [
        account.get("id"),
        account.get("name"),
        account.get("biz_id"),
        account.get("created_at"),
        account.get("updated_at"),
        account.get("created_by_id"),
        account.get("updated_by_id"),
        account.get("deleted_by_id"),
        account.get("initial_balance")
    ]

def add_accounts_to_sheet(accounts, sheet_name="Accounts"):
    client = authorize_google_sheets()
    if client is None:
        print("Не удалось авторизоваться. Операция прервана.")
        return

    sheet = client.open_by_url(SHEET_URL)

    try:
        worksheet = sheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Лист '{sheet_name}' не найден. Создаём новый лист...")
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    headers = [
        "ID счета",             # account.get("id")
        "Название счета",       # account.get("name")
        "ID бизнеса",           # account.get("biz_id")
        "Дата создания",        # account.get("created_at")
        "Дата обновления",      # account.get("updated_at")
        "ID создателя",         # account.get("created_by_id")
        "ID обновившего",       # account.get("updated_by_id")
        "ID удалившего",        # account.get("deleted_by_id")
        "Начальный баланс"      # account.get("initial_balance")
    ]

    if not worksheet.row_values(1):
        print("Добавляем заголовки в таблицу...")
        worksheet.update('A1:I1', [headers])

    existing_ids = set(worksheet.col_values(1)[1:])
    new_accounts = [tx for tx in accounts if str(tx.get("id")) not in existing_ids]

    if not new_accounts:
        print("Нет новых счетов для добавления.")
        return

    rows = [format_account(tx) for tx in new_accounts]

    try:
        worksheet.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"Добавлено {len(rows)} новых счетов.")
    except Exception as e:
        print(f"Ошибка при добавлении строк: {e}")

if __name__ == "__main__":
    biz_id = 17937
    accounts = fetch_accounts(biz_id)
    add_accounts_to_sheet(accounts)