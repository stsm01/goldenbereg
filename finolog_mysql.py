import requests
import pymysql

config = {
    "host": "localhost",
    "user": "root",
    "password": "Stas007blin!",
    "database": "mysql",
    "charset": "utf8mb4"
}

api_key = 'sMF6bh3f2Sz1KGa835dd392992c820482eec868a169d6871UbesQOtdDvDH3fbs'
headers = {'Api-Token': api_key, 'Content-Type': 'application/json'}
biz_id = '17937'
url = f'https://api.finolog.ru/v1/biz/{biz_id}/transaction'

conn = pymysql.connect(**config)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INT PRIMARY KEY,
        biz_id INT,
        type VARCHAR(10),
        transfer_id INT,
        project_id INT,
        order_id INT,
        is_multi_transfer BOOLEAN,
        status VARCHAR(10),
        date DATETIME,
        report_date DATETIME,
        value DECIMAL(20,4),
        base_value DECIMAL(20,4),
        description TEXT,
        category_id INT,
        category_type VARCHAR(30) NULL,
        category_activities VARCHAR(20),
        category_code VARCHAR(20),
        category_cash_in_out BOOLEAN,
        category_interest_repayment BOOLEAN,
        company_ids VARCHAR(255),
        account_id INT,
        contractor_id VARCHAR(255),
        requisite_id VARCHAR(255),
        project_ids VARCHAR(255),
        order_ids VARCHAR(255),
        order_type VARCHAR(10),
        created_at DATETIME,
        updated_at DATETIME,
        deleted_at DATETIME,
        created_by_id INT,
        updated_by_id INT,
        deleted_by_id INT,
        is_splitted BOOLEAN,
        split_id INT,
        payment_id INT,
        schedule_id INT,
        source_id INT,
        is_debt BOOLEAN,
        has_comments BOOLEAN,
        payment_number VARCHAR(255),
        vat DECIMAL(20,4),
        base_vat DECIMAL(20,4),
        autoeditor_id INT,
        original_schedule_id INT
    )
''')

def get_transactions_data(page, start_date, end_date):
    params = {
        'page': page,
        'start_date': start_date,
        'end_date': end_date,
        'per_page': 200
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        transactions_data = response.json()
        return transactions_data
    else:
        return []

start_date = '2022-01-01'
end_date = '2023-05-06'
max_rows = 500
per_page = 200
row_counter = 0
page = 1

while True:
    transactions_data = get_transactions_data(page, start_date, end_date)
    if not transactions_data:
        break

    for transaction in transactions_data:
        try:
            cur.execute("SELECT id FROM transactions WHERE id = %s", (transaction["id"],))
            record_exists = cur.fetchone() is not None
            if record_exists:
                continue
            else:
                insert_query = """
                                    INSERT INTO finolog_transactions (
                                        id, biz_id, type, transfer_id, project_id, order_id,
                                        is_multi_transfer, status, date, report_date, value, base_value,
                                        description, category_id, category_type, category_activities,
                                        category_code, category_cash_in_out, category_interest_repayment,
                                        company_ids, account_id, contractor_id, requisite_id, project_ids,
                                        order_ids, order_type, created_at, updated_at, deleted_at,
                                        created_by_id, updated_by_id, deleted_by_id, is_splitted, split_id,
                                        payment_id, schedule_id, source_id, is_debt, has_comments,
                                        payment_number, vat, base_vat, autoeditor_id, original_schedule_id
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                cur.execute(insert_query, (
                    transaction.get('id', None),
                    transaction.get('biz_id', None),
                    transaction.get('type', None),
                    transaction.get('transfer_id', None),
                    transaction.get('project_id', None),
                    transaction.get('order_id', None),
                    transaction.get('is_multi_transfer', None),
                    transaction.get('status', None),
                    transaction.get('date', None),
                    transaction.get('report_date', None),
                    transaction.get('value', None),
                    transaction.get('base_value', None),
                    transaction.get('description', None),
                    transaction.get('category_id', None),
                    transaction.get('category_type', None),
                    transaction.get('category_activities', None),
                    transaction.get('category_code', None),
                    transaction.get('category_cash_in_out', None),
                    transaction.get('category_interest_repayment', None),
                    transaction.get('company_ids', None),
                    transaction.get('account_id', None),
                    transaction.get('contractor_id', None),
                    transaction.get('requisite_id', None),
                    transaction.get('project_ids', None),
                    transaction.get('order_ids', None),
                    transaction.get('order_type', None),
                    transaction.get('created_at', None),
                    transaction.get('updated_at', None),
                    transaction.get('deleted_at', None),
                    transaction.get('created_by_id', None),
                    transaction.get('updated_by_id', None),
                    transaction.get('deleted_by_id', None),
                    transaction.get('is_splitted', None),
                    transaction.get('split_id', None),
                    transaction.get('payment_id', None),
                    transaction.get('schedule_id', None),
                    transaction.get('source_id', None),
                    transaction.get('is_debt', None),
                    transaction.get('has_comments', None),
                    transaction.get('payment_number', None),
                    transaction.get('vat', None),
                    transaction.get('base_vat', None),
                    transaction.get('autoeditor_id', None),
                    transaction.get('original_schedule_id', None)
                ))
            conn.commit()
            row_counter += 1
            if row_counter >= max_rows:
                break
        except Exception as e:
            print(f"Error adding transaction with id {transaction['id']}: {e}")

    if len(transactions_data) < per_page:
        break

    page += 1

cur.close()
conn.close()
