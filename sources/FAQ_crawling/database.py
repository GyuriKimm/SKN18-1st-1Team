import pymysql


class Database:
    def __init__(self, host, port, user, password, db, table) -> None:
        self.connection = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.table = table

    def connect(self):
        """데이터베이스와 연결"""
        try:
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, 
                                              database=self.db, charset="utf8")
        except Exception as e:
            print("Connection error")
        else:
            print("connected!")

    def insert(self, data):
        """연결된 데이터베이스에 데이터 삽입"""
        cur = self.connection.cursor()
        query = f"INSERT INTO {self.table} (company, category, question, answer) VALUES(%s, %s, %s, %s);"
        try:
            cur.executemany(query, data)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def delete(self):
        """연결된 데이터베이스에 데이터 삭제"""
        cur = self.connection.cursor()
        query = f"DELETE FROM {self.table}"
        try:
            cur.execute(query)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            self.logger.warning(f"Deletion failed: {e}")
            raise e
        else:
            self.logger.info(f"Successfully delete {self.table} table")

    def read_data(self):
        """연결된 데이터베이스에 데이터 읽기"""
        cur = self.connection.cursor()
        query = f"SELECT * FROM {self.table}"
        try:
            cur.execute(query)
        except Exception as e:
            raise e
        return cur.fetchall()

    def close_connection(self):
        """연결 종료"""
        if self.connection:
            self.connection.close()
