import mysql.connector
from config import *

config = {
    'user': database_user,
    'password': database_password,
    'host': 'localhost',
    'database': database
}

def create_database(db_name):
    config = {'user': database_user, 'password': database_password, 'host': 'localhost'}
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = f"DROP DATABASE IF EXISTS {db_name}"
    cursor.execute(SQL_Query)
    SQL_Query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
    cursor.execute(SQL_Query)
    conn.commit()
    cursor.close()
    conn.close()
    print(f'Database {db_name} created successfully')


# Table CUSTOMER
def create_customer_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = """CREATE TABLE IF NOT EXISTS CUSTOMER (
                    `CHAT_ID`     BIGINT NOT NULL UNIQUE,
                    `NAME`        VARCHAR(20),
                    `LAST_NAME`   VARCHAR(25) NOT NULL,
                    `PHONE`       VARCHAR(13) NOT NULL,
                    `ADDRESS`     TEXT NOT NULL,
                    PRIMARY KEY (`CHAT_ID`)
                  );"""
    cursor.execute(SQL_Query)
    conn.commit()
    cursor.close()
    conn.close()
    print('Customer table created successfully')


# Table PRODUCT
def create_product_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = """CREATE TABLE IF NOT EXISTS PRODUCT (
                    `ID`                INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    `NAME`              VARCHAR(50) NOT NULL,
                    `DESCRIPTION`       VARCHAR(100),
                    `PRICE`             DOUBLE NOT NULL,
                    `INVENTORY`         MEDIUMINT NOT NULL DEFAULT 0, 
                    `FILE_ID`           VARCHAR(100)                          
                  );"""
    cursor.execute(SQL_Query)
    conn.commit()
    cursor.close()
    conn.close()
    print('Product table created successfully')


# Table SALE
def create_sale_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = """CREATE TABLE IF NOT EXISTS SALE (
                    `ID`                INT NOT NULL AUTO_INCREMENT,
                    `CUSTOMER_ID`      BIGINT NOT NULL,
                    `PRODUCT_ID`       INT UNSIGNED NOT NULL,
                    `QUANTITY`         INT NOT NULL,
                    PRIMARY KEY (`ID`),
                    FOREIGN KEY (`CUSTOMER_ID`) REFERENCES CUSTOMER(`CHAT_ID`),
                    FOREIGN KEY (`PRODUCT_ID`) REFERENCES PRODUCT(`ID`)
                  );"""
    cursor.execute(SQL_Query)
    conn.commit()
    cursor.close()
    conn.close()
    print('Sale table created successfully')


# Table INVOICES
def create_invoices_table():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    SQL_Query = """CREATE TABLE IF NOT EXISTS INVOICES (
                    `SALE_ID`           INT NOT NULL,
                    `PRODUCT_ID`        INT UNSIGNED NOT NULL,
                    `QUANTITY`          TINYINT UNSIGNED NOT NULL,
                    `CUSTOMERS_ID`      BIGINT NOT NULL,
                    PRIMARY KEY (`SALE_ID`, `PRODUCT_ID`),
                    FOREIGN KEY (`SALE_ID`) REFERENCES SALE(`ID`),
                    FOREIGN KEY (`PRODUCT_ID`) REFERENCES PRODUCT(`ID`),
                    FOREIGN KEY (`CUSTOMERS_ID`) REFERENCES CUSTOMER(`CHAT_ID`)
                  );"""
    cursor.execute(SQL_Query)
    conn.commit()
    cursor.close()
    conn.close()
    print('Invoices table created successfully')


if __name__ == "__main__":
    create_database(database)
    create_customer_table()
    create_product_table()
    create_sale_table()
    create_invoices_table()