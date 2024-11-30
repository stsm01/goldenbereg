import datetime
import logging
from transactions import fetch_all_transactions, update_google_sheet
from categories import fetch_categories, add_categories_to_sheet
from accounts import fetch_accounts, add_accounts_to_sheet
from groups import fetch_groups, add_groups_to_sheet
from src.config import SHEET_URL

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,                # Уровень логгирования (INFO и выше)
    filename='update.log',             # Имя файла, куда сохраняются логи
    filemode='a',                      # Режим записи (a = append, добавлять записи в конец)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщений
)

# Параметры
TRANSACTIONS_SHEET_NAME = "Transactions"
CATEGORIES_SHEET_NAME = "Categories"
ACCOUNTS_SHEET_NAME = "Accounts"
GROUPS_SHEETS_NAME = "Groups"
BIZ_ID = 17937

def main():
    """
    Основная функция для обновления данных Google Таблицы.
    """
    try:
        logging.info("Запуск обновления...")

        # Обновление транзакций
        try:
            logging.info("Начинаем обновление транзакций...")
            transactions = fetch_all_transactions(BIZ_ID)
            if transactions:
                update_google_sheet(TRANSACTIONS_SHEET_NAME, transactions)
                logging.info(f"Успешно обновлено {len(transactions)} транзакций.")
            else:
                logging.info("Нет транзакций для обновления.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении транзакций: {e}")

        # Обновление категорий
        try:
            logging.info("Начинаем обновление категорий...")
            categories = fetch_categories(BIZ_ID)
            if categories:
                add_categories_to_sheet(categories, CATEGORIES_SHEET_NAME)
                logging.info(f"Успешно обновлено {len(categories)} категорий.")
            else:
                logging.info("Нет категорий для обновления.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении категорий: {e}")

        # Обновление счетов
        try:
            logging.info("Начинаем обновление счетов...")
            accounts = fetch_accounts(BIZ_ID)
            if accounts:
                add_accounts_to_sheet(accounts, ACCOUNTS_SHEET_NAME)
                logging.info(f"Успешно обновлено {len(accounts)} счетов.")
            else:
                logging.info("Нет счетов для обновления.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении счетов: {e}")

        # Обновление групп
        try:
            logging.info("Начинаем обновление групп...")
            groups = fetch_groups(BIZ_ID)
            if groups:
                add_groups_to_sheet(groups, GROUPS_SHEETS_NAME)
                logging.info(f"Успешно обновлено {len(groups)} групп.")
            else:
                logging.info("Нет групп для обновления.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении групп: {e}")

        logging.info("Обновление завершено успешно!")

    except Exception as e:
        logging.critical(f"Критическая ошибка в процессе обновления: {e}")

if __name__ == "__main__":
    main()