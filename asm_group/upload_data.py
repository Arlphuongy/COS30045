import pandas as pd
from sqlalchemy import create_engine

# Connection string từ Railway
username = "root"
password = "jFogxuARgjfLXVKooYCqgXFqHaAmvarl"
host = "shuttle.proxy.rlwy.net"
port = 58689
database = "railway"

# Kết nối tới MySQL
connection_str = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_str)

tables = {
    "agri": "OECD_dashboard\\data\\agri_cleaned.csv",
    "area": "OECD_dashboard\\data\\area_cleaned.csv",
    "energy": "OECD_dashboard\\data\\energy_cleaned.csv",
    "water": "OECD_dashboard\\data\\water_cleaned.csv"
}

# Upload
for table_name, file_name in tables.items():
    try:
        df = pd.read_csv(file_name)
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"✅ Uploaded {file_name} to MySQL table `{table_name}`")
    except Exception as e:
        print(f"❌ Failed to upload {file_name}: {e}")