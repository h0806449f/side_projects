import pymysql

# 連接到 RDS MySQL 資料庫
connection = pymysql.connect(
    # for source
    # host="terraform-20250302051229305100000001.c98qk102ncqc.ap-northeast-1.rds.amazonaws.com",  # Source DB
    # database="source_db",
    #
    # for target
    host="terraform-20250302051229305100000002.c98qk102ncqc.ap-northeast-1.rds.amazonaws.com",  # Target DB
    database="target_db",
    #
    # general setting
    user="henry",
    password="12345678",
    port=3306,
)


def get_tables(cursor):
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    return tables


def get_columns(cursor, table_name):
    cursor.execute(f"DESCRIBE {table_name};")
    columns = cursor.fetchall()
    return columns


def select_from_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
    data = cursor.fetchall()
    return data


try:
    with connection.cursor() as cursor:
        # 查詢資料庫中所有的表格
        tables = get_tables(cursor)

        if not tables:
            print("no table")
        else:
            for table in tables:
                table_name = table[0]
                print(f"Table: {table_name}")

                # 查詢表格的欄位
                columns = get_columns(cursor, table_name)

                if not columns:
                    print(f"table {table_name} no column")
                else:
                    print("Columns:")
                    for column in columns:
                        print(f"  - {column[0]}")  # 這裡取得每個欄位名稱

                    # 查詢表格的前 10 條資料
                    data = select_from_table(cursor, table_name)
                    print(f"Data from {table_name}:")
                    for row in data:
                        print(row)
                print("=" * 40)

finally:
    connection.close()
