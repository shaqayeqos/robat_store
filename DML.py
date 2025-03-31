import mysql.connector
from config import *
config = {'user': database_user , 'password': database_password , 'host': 'localhost', 'database': database }

#customer
def insert_customer_data(NAME, LAST_NAME, PHONE, ADDRESS, CHAT_ID):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = "INSERT IGNORE INTO CUSTOMER (NAME, LAST_NAME, PHONE, ADDRESS, CHAT_ID) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(SQL_Query, (NAME, LAST_NAME, PHONE, ADDRESS, CHAT_ID))
    user_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return user_id

#sale
def insert_sale_data(customer_id, product_id, quantity):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = "INSERT INTO SALE (CUSTOMER_ID, PRODUCT_ID, QUANTITY) VALUES (%s, %s, %s);"
    cursor.execute(SQL_Query, (customer_id, product_id, quantity))
    sale_id = cursor.lastrowid 
    conn.commit()
    cursor.close()
    conn.close()
    return sale_id
    
    
    
#product
def insert_product_info(NAME, PRICE, INVENTORY, DESCRIPTION, FILE_ID):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = "INSERT IGNORE INTO PRODUCT (NAME, PRICE, INVENTORY, DESCRIPTION, FILE_ID) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(SQL_Query, (NAME, PRICE, INVENTORY, DESCRIPTION, FILE_ID))
    product_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return product_id

#invoice
def insert_invoice_data(SALE_ID, PRODUCT_ID, QUANTITY, CUSTOMERS_ID):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = "INSERT IGNORE INTO INVOICES (SALE_ID, PRODUCT_ID, QUANTITY, CUSTOMERS_ID) VALUES (%s, %s, %s, %s);"
    cursor.execute(SQL_Query, (SALE_ID, PRODUCT_ID, QUANTITY, CUSTOMERS_ID))
    conn.commit() 
    cursor.close()
    conn.close()
    return 
    



    