#전기차 충전소 현황을 엑셀에서 DB로 올리는 코드
import pandas as pd
import pymysql
from datetime import datetime
import re

def create_table_if_not_exists():
    """Create the table with charging speed and region columns"""
    connection = pymysql.connect(
        host="localhost", 
        port=3306, 
        user="urstory", 
        password="1234", 
        database="examplesdb", 
        charset="utf8"
    )
    cur = connection.cursor()
    
    # First, let's read the data to get real column names
    df = pd.read_excel(
        r"C:\dev\study\python\web_crawl\source\충전기구축현황.xlsx",  # Change to your file name
        engine='openpyxl', 
        header=3
    )
    
    # Clean column names
    df.columns = df.columns.astype(str).str.strip()
    
    # Get region columns (all except first two and last)
    region_cols = df.columns[2:-1]  # Exclude first (date), second (charging speed), and last (sum)
    
    # Clean region names for MySQL
    cleaned_region_cols = [clean_column_name(region) for region in region_cols]
    
    print("📋 Original region names:")
    for i, (original, cleaned) in enumerate(zip(region_cols, cleaned_region_cols)):
        print(f"   {original} -> {cleaned}")
    
    # Create dynamic SQL for table creation
    columns_sql = []
    for cleaned_region in cleaned_region_cols:
        columns_sql.append(f"`{cleaned_region}` INT")
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS charging_station_by_region (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `date_recorded` DATE,
        `charging_speed` VARCHAR(10),
        {', '.join(columns_sql)},
        `sum_total` INT,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY `unique_date_speed` (`date_recorded`, `charging_speed`)
    );
    """
    
    print("\n🔧 Creating table with SQL:")
    print(create_table_sql)
    
    cur.execute(create_table_sql)
    connection.commit()
    connection.close()
    print("✅ Table created/verified successfully!")
    
    return region_cols, cleaned_region_cols

def clean_column_name(name):
    """Clean column name for MySQL compatibility"""
    # Remove special characters and spaces, keep only alphanumeric and underscore
    cleaned = re.sub(r'[^a-zA-Z0-9가-힣_]', '_', str(name))
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Ensure it starts with a letter or underscore
    if cleaned and not cleaned[0].isalpha():
        cleaned = 'region_' + cleaned
    return cleaned

def db_insert(data, region_cols, cleaned_region_cols):
    """Insert data into MySQL database"""
    print(f"📊 Inserting {len(data)} records...")
    
    connection = pymysql.connect(
        host="localhost", 
        port=3306, 
        user="urstory", 
        password="1234", 
        database="examplesdb", 
        charset="utf8"
    )
    cur = connection.cursor()
    
    # Create placeholders for the INSERT query
    placeholders = ['%s'] * (len(cleaned_region_cols) + 3)  # +3 for date, charging_speed, and sum
    placeholders_str = ', '.join(placeholders)
    
    # Create column names with backticks for MySQL
    column_names = ['`date_recorded`', '`charging_speed`'] + [f'`{col}`' for col in cleaned_region_cols] + ['`sum_total`']
    
    query = f"""
    INSERT INTO charging_station_by_region 
    ({', '.join(column_names)}) 
    VALUES ({placeholders_str})
    ON DUPLICATE KEY UPDATE
    {', '.join([f'`{col}` = VALUES(`{col}`)' for col in cleaned_region_cols])},
    `sum_total` = VALUES(`sum_total`)
    """
    
    print(" Using INSERT query:")
    print(query)
    
    try:
        cur.executemany(query, data)
        connection.commit()
        print(f"✅ Successfully inserted {len(data)} records!")
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        connection.rollback()
    finally:
        connection.close()

def get_charging_station_data(region_cols, cleaned_region_cols):
    """Extract and process the charging station Excel data"""
    
    # Read Excel file starting from row 4 (index 3)
    df = pd.read_excel(
        r"C:\dev\study\python\web_crawl\source\충전기구축현황.xlsx",  # Change to your file name
        engine='openpyxl', 
        header=3
    )
    
    print(f"📋 Original data shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Clean column names
    df.columns = df.columns.astype(str).str.strip()
    
    # Get the date column (first column)
    date_col = df.columns[0]
    
    # Get charging speed column (second column)
    speed_col = df.columns[1]
    
    # Get sum column (last column)
    sum_col = df.columns[-1]
    
    print(f" Date column: {date_col}")
    print(f"⚡ Charging speed column: {speed_col}")
    print(f"📊 Sum column: {sum_col}")
    
    # Prepare data for insertion
    data = []
    
    for _, row in df.iterrows():
        # Get the date
        date_str = str(row[date_col]).strip()
        
        # Skip if date is empty or invalid
        if pd.isna(date_str) or date_str == 'nan' or date_str == '':
            continue
            
        # Get charging speed
        speed_str = str(row[speed_col]).strip()
        if pd.isna(speed_str) or speed_str == 'nan' or speed_str == '':
            continue
            
        # Convert date string to proper format
        try:
            if '-' in date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m')
            elif '/' in date_str:
                date_obj = datetime.strptime(date_str, '%Y/%m')
            else:
                date_obj = datetime.strptime(date_str, '%Y%m')
        except:
            print(f"⚠️ Could not parse date: {date_str}")
            continue
        
        # Get region values
        region_values = []
        for region in region_cols:
            station_count = row[region]
            if pd.isna(station_count) or station_count == '':
                region_values.append(0)
            else:
                try:
                    region_values.append(int(station_count))
                except:
                    region_values.append(0)
        
        # Get sum value
        sum_value = row[sum_col]
        if pd.isna(sum_value) or sum_value == '':
            sum_value = 0
        else:
            try:
                sum_value = int(sum_value)
            except:
                sum_value = 0
        
        # Create data tuple: (date, charging_speed, region1_value, region2_value, ..., regionN_value, sum)
        data_tuple = (date_obj.date(), speed_str) + tuple(region_values) + (sum_value,)
        data.append(data_tuple)
        
        print(f"⚡ {date_obj.date()} - {speed_str}: {dict(zip(region_cols, region_values))} -> Sum: {sum_value}")
    
    print(f"\n📊 Total records to insert: {len(data)}")
    return data

def main():
    """Main function"""
    print("🚀 Starting charging station data extraction and upload...")
    
    # Create table if it doesn't exist and get region names
    region_cols, cleaned_region_cols = create_table_if_not_exists()
    
    # Get and process data
    data = get_charging_station_data(region_cols, cleaned_region_cols)
    
    if data:
        # Insert data into database
        db_insert(data, region_cols, cleaned_region_cols)
        print("🎉 Charging station data upload completed successfully!")
    else:
        print("❌ No data to insert!")

if __name__ == "__main__":
    main()