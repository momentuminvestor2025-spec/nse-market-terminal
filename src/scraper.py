import httpx
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NSEScraper:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        # Mirroring authentic 2026 enterprise system signatures
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.nseindia.com/"
        }
        
    def _get_live_session_cookies(self) -> httpx.Cookies:
        """Establishes security handshake context to bypass advanced bot blocks."""
        with httpx.Client(headers=self.headers, timeout=15.0, follow_redirects=True) as client:
            # Hit the home page first to capture structural session tokens
            response = client.get(self.base_url)
            return response.cookies

    def fetch_52w_highs(self) -> pd.DataFrame:
        url = "https://www.nseindia.com/api/live-analysis-52week-high-low?index=high"
        try:
            cookies = self._get_live_session_cookies()
            with httpx.Client(headers=self.headers, cookies=cookies, timeout=20.0) as client:
                res = client.get(url)
                if res.status_code != 200:
                    logging.error(f"NSE 52W High returned HTTP Error Code {res.status_code}")
                    return pd.DataFrame()
                
                raw_data = res.json().get('data', [])
                if not raw_data:
                    return pd.DataFrame()
                
                processed_records = []
                today_str = datetime.today().strftime('%Y-%m-%d')
                for row in raw_data:
                    processed_records.append({
                        "symbol": row.get('symbol'),
                        "company_name": row.get('pName', row.get('symbol')),
                        "current_price": float(str(row.get('lastPrice', 0)).replace(',', '')),
                        "snapshot_date": today_str
                    })
                return pd.DataFrame(processed_records)
        except Exception as e:
            logging.error(f"Exception handling execution on 52W Scraper: {str(e)}")
            return pd.DataFrame()

    def fetch_most_active(self) -> pd.DataFrame:
        url = "https://www.nseindia.com/api/live-analysis-most-active-securities?index=volume"
        try:
            cookies = self._get_live_session_cookies()
            with httpx.Client(headers=self.headers, cookies=cookies, timeout=20.0) as client:
                res = client.get(url)
                if res.status_code != 200:
                    return pd.DataFrame()
                
                raw_data = res.json().get('data', [])
                processed_records = []
                today_str = datetime.today().strftime('%Y-%m-%d')
                for row in raw_data:
                    processed_records.append({
                        "symbol": row.get('symbol'),
                        "company_name": row.get('symbol'), 
                        "volume": int(str(row.get('quantity', 0)).replace(',', '')),
                        "turnover_crores": float(str(row.get('value', 0)).replace(',', '')),
                        "snapshot_date": today_str
                    })
                return pd.DataFrame(processed_records)
        except Exception as e:
            logging.error(f"Exception handling execution on Most Active Scraper: {str(e)}")
            return pd.DataFrame()