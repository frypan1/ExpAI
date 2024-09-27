import mysql.connector
import os
from mysql.connector import Error

def insert_into_database(expense_details_list):
    """
    Insert the parsed invoice details into the MySQL database.
    """
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='test',
            user='root',
            password=os.getenv('DATABASE_PASSWORD')
        )

        if conn.is_connected():
            cursor = conn.cursor()
            sql_insert_query = """
            INSERT INTO expense_deets (expense_date, category, amount, product_name)
            VALUES (%s, %s, %s, %s)
            """

            for expense_details in expense_details_list:
                insert_data = (
                    expense_details['Date'],
                    expense_details['Category'],
                    float(expense_details['Amount']),
                    expense_details['Product Name']
                )
                cursor.execute(sql_insert_query, insert_data)

            conn.commit()
            print(f"{cursor.rowcount} records inserted successfully into expense_deets table.")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")