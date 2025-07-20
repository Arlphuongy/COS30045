# utils/db.py

import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

@st.cache_resource
def get_db_engine():
    username = "root"
    password = "jFogxuARgjfLXVKooYCqgXFqHaAmvarl"
    host = "shuttle.proxy.rlwy.net"
    port = 58689
    database = "railway"

    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string)

@st.cache_data
def load_table(table_name):
    engine = get_db_engine()
    query = text(f"SELECT * FROM {table_name}")

    with engine.connect() as connection:
        df = pd.read_sql(query, con=connection)

    return df