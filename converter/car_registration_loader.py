import pandas as pd
import pymysql

# 공통 DB 설정
DB_CONFIG = {
    "host": "",
    "port": 3306,
    "user": "",
    "password": "",
    "database": "",
    "charset": "utf8"
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


# ✅ 공통 유틸
def clean_value(val):
    if pd.isna(val) or val == "-":
        return None
    return float(str(val).replace(",", ""))


def load_excel(filepath, header=2):
    df = pd.read_excel(filepath, engine='openpyxl', header=header)
    df.columns = df.columns.map(str).str.strip()
    df.index = df.iloc[:, 0].astype(str).str.strip()
    return df.drop(df.columns[0], axis=1)


# ✅ 1. 지역별 등록
def create_region_tables():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS region (
                region_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_registration_by_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT,
                registered_cars INT,
                region_id INT,
                FOREIGN KEY (region_id) REFERENCES region(region_id)
            );
        """)
        conn.commit()


def insert_regions(region_names):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany("INSERT IGNORE INTO region (name) VALUES (%s)", [(r,) for r in region_names])
        conn.commit()


def get_region_map():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT region_id, name FROM region")
        return {name: rid for rid, name in cur.fetchall()}


def load_region_data():
    df = load_excel("../docs/시도별 자동차 등록 현황.xlsx")
    regions = df.index.tolist()[1:-2]
    create_region_tables()
    insert_regions(regions)
    region_map = get_region_map()

    data = []
    for year in df.columns:
        for region in regions:
            val = clean_value(df.loc[region, year])
            if val is not None:
                data.append((int(year), int(val), region_map[region]))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO car_registration_by_region (year, registered_cars, region_id) VALUES (%s, %s, %s)",
            data
        )
        conn.commit()
    print(f"[지역별 등록] {len(data)}건 삽입 완료")


# ✅ 2. 차종별 등록
def create_car_type_table():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_type_registration (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT,
                passenger_car FLOAT,
                van_car FLOAT,
                truck_car FLOAT,
                special_car FLOAT
            );
        """)
        conn.commit()


def load_car_type_data():
    df = load_excel("../docs/차종별 자동차 등록 현황.xlsx")
    car_types = ['승용차', '승합차', '화물차', '특수차']
    create_car_type_table()

    data = []
    for year in df.columns[1:]:
        row = df.loc[car_types, year].map(clean_value)
        data.append((int(year), *row))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO car_type_registration (year, passenger_car, van_car, truck_car, special_car) VALUES (%s, %s, %s, %s, %s)",
            data
        )
        conn.commit()
    print(f"[차종별 등록] {len(data)}건 삽입 완료")


# ✅ 3. 용도별 등록
def create_usage_table():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_use_type_registration (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT,
                official FLOAT,
                private FLOAT,
                business FLOAT
            );
        """)
        conn.commit()


def load_usage_data():
    df = load_excel("../docs/용도별 자동차 등록 현황.xlsx")
    usage_types = ['관용', '자가용', '영업용']
    create_usage_table()

    data = []
    for year in df.columns[1:]:
        row = df.loc[usage_types, year].map(clean_value)
        data.append((int(year), *row))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO car_use_type_registration (year, official, private, business) VALUES (%s, %s, %s, %s)",
            data
        )
        conn.commit()
    print(f"[용도별 등록] {len(data)}건 삽입 완료")


# ✅ 메인 실행
def main():
    load_region_data()
    load_car_type_data()
    load_usage_data()


if __name__ == "__main__":
    main()
