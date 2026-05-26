import pandas as pd
from src.database import DatabaseManager

class AnalyticsEngine:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_tab1_dataset(self, selected_date: str) -> pd.DataFrame:
        """Fetches dynamic 52W highs joined with multi-month historical lookbacks."""
        query = """
        WITH current_day AS (
            SELECT h.symbol, m.company_name, h.current_price, h.snapshot_date, m.first_seen_date
            FROM daily_52week_high h
            JOIN stocks_master m ON h.symbol = m.symbol
            WHERE h.snapshot_date = :selected_date
        ),
        counts AS (
            SELECT symbol, COUNT(*) as historical_count
            FROM daily_52week_high
            WHERE snapshot_date <= :selected_date
            GROUP BY symbol
        )
        SELECT 
            c.symbol as "Symbol",
            c.company_name as "Company Name",
            c.current_price as "Price (₹)",
            c.snapshot_date as "Date",
            cnt.historical_count as "Historical Appearances",
            CASE WHEN c.first_seen_date = c.snapshot_date THEN 'NEW' ELSE 'RETURNING' END as "Status"
        FROM current_day c
        JOIN counts cnt ON c.symbol = cnt.symbol
        ORDER BY cnt.historical_count DESC;
        """
        with self.db.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"selected_date": selected_date})

    def get_symbol_occurrence_history(self, symbol: str) -> pd.DataFrame:
        """Pulls chronological run-lists of specific asset breakouts."""
        query = """
        SELECT snapshot_date as "Appeared Date", current_price as "Closing Price (₹)"
        FROM daily_52week_high
        WHERE symbol = :symbol
        ORDER BY snapshot_date DESC;
        """
        with self.db.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"symbol": symbol})

    def get_tab2_dataset(self) -> pd.DataFrame:
        """Aggregates master-level analytics for institutional breakdown."""
        query = """
        SELECT 
            h.symbol as "Symbol",
            m.company_name as "Company Name",
            COUNT(*) as "Total Breakout Days",
            MAX(h.snapshot_date) as "Latest Breakout Date"
        FROM daily_52week_high h
        JOIN stocks_master m ON h.symbol = m.symbol
        GROUP BY h.symbol, m.company_name
        ORDER BY "Total Breakout Days" DESC, "Latest Breakout Date" DESC;
        """
        with self.db.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_tab3_dataset(self, selected_date: str) -> pd.DataFrame:
        """Executes full historical overlap matrix correlation."""
        query = """
        SELECT 
            a.symbol as "Symbol",
            a.volume as "Volume (Shares)",
            a.turnover_crores as "Turnover (Cr)",
            a.snapshot_date as "Date",
            CASE WHEN h.symbol IS NOT NULL THEN 'OVERLAP MATCH' ELSE 'ISOLATED' END as "52W High Match",
            (SELECT COUNT(*) FROM daily_most_active WHERE symbol = a.symbol AND snapshot_date <= :selected_date) as "Historical Active Days"
        FROM daily_most_active a
        LEFT JOIN daily_52week_high h ON a.symbol = h.symbol AND a.snapshot_date = h.snapshot_date
        WHERE a.snapshot_date = :selected_date
        ORDER BY a.volume DESC;
        """
        with self.db.engine.connect() as conn:
            return pd.read_sql(query, conn, params={"selected_date": selected_date})