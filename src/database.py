import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

class DatabaseManager:
    def __init__(self):
        raw_url = st.secrets.get("database", {}).get("DATABASE_URL") or os.getenv("DATABASE_URL")
        if not raw_url:
            raise ValueError("CRITICAL ERROR: DATABASE_URL configuration missing.")
        
        # Enforce standard postgresql dialect string
        if raw_url.startswith("postgresql+pg8000://"):
            self.db_url = raw_url.replace("postgresql+pg8000://", "postgresql://", 1)
        else:
            self.db_url = raw_url

        # Configure connection pool optimizations using standard psycopg2 settings
        self.engine = create_engine(
            self.db_url,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            pool_pre_ping=True
        )

    def execute_query(self, query: str, params: dict = None):
        with self.engine.connect() as conn:
            return conn.execute(text(query), params or {})

    def upsert_stocks_master(self, df_stocks: pd.DataFrame):
        """Inserts unique records into stock master and checks for first seen indicators."""
        query = """
        INSERT INTO stocks_master (symbol, company_name, first_seen_date)
        VALUES (:symbol, :company_name, :snapshot_date)
        ON CONFLICT (symbol) DO NOTHING;
        """
        with self.engine.begin() as conn:
            for _, row in df_stocks.iterrows():
                conn.execute(text(query), {
                    "symbol": row['symbol'],
                    "company_name": row['company_name'],
                    "snapshot_date": row['snapshot_date']
                })

    def save_52w_highs(self, df: pd.DataFrame):
        if df.empty: 
            return
        self.upsert_stocks_master(df)
        query = """
        INSERT INTO daily_52week_high (symbol, current_price, snapshot_date)
        VALUES (:symbol, :current_price, :snapshot_date)
        ON CONFLICT (symbol, snapshot_date) DO NOTHING;
        """
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text(query), {
                    "symbol": row['symbol'],
                    "current_price": row['current_price'],
                    "snapshot_date": row['snapshot_date']
                })

    def save_most_active(self, df: pd.DataFrame):
        if df.empty: 
            return
        self.upsert_stocks_master(df)
        query = """
        INSERT INTO daily_most_active (symbol, volume, turnover_crores, snapshot_date)
        VALUES (:symbol, :volume, :turnover_crores, :snapshot_date)
        ON CONFLICT (symbol, snapshot_date) DO NOTHING;
        """
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text(query), {
                    "symbol": row['symbol'],
                    "volume": row['volume'],
                    "turnover_crores": row['turnover_crores'],
                    "snapshot_date": row['snapshot_date']
                })
