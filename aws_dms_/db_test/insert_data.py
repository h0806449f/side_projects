import pymysql

# RDS 連接設定
connection = pymysql.connect(
    host="terraform-20250302051229305100000001.c98qk102ncqc.ap-northeast-1.rds.amazonaws.com",  # RDS 端點
    user="henry",  # 資料庫用戶
    password="12345678",  # 資料庫密碼
    database="source_db",  # 目標資料庫名稱
    port=3306,  # MySQL 默認端口
    cursorclass=pymysql.cursors.DictCursor,  # 讓結果以字典方式返回
)

try:
    with connection.cursor() as cursor:
        # 建立 table 的 SQL 查詢
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS people (
            NAME VARCHAR(100),
            BIRTH DATE,
            GENDER VARCHAR(10)
        );
        """
        cursor.execute(create_table_sql)

        # 插入資料的 SQL 查詢
        insert_sql = """
        INSERT INTO people (NAME, BIRTH, GENDER) 
        VALUES (%s, %s, %s);
        """
        values = ("henry", "1991-05-02", "male")
        cursor.execute(insert_sql, values)

        # 提交到資料庫
        connection.commit()

        # 查詢並顯示插入的資料
        select_sql = "SELECT * FROM people LIMIT 10;"
        cursor.execute(select_sql)
        result = cursor.fetchall()
        print(result)

finally:
    # 關閉連接
    connection.close()
