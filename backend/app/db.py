from pathlib import Path
import sqlite3
import json

data_path = Path(__file__).resolve().parent / 'data'
data_path.mkdir(parents=True, exist_ok=True)
db_name = 'query.db'
db_path = Path(data_path) / db_name

def init_db() -> None:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            user_id INTEGER,
            city TEXT NOT NULL,
            weather_data JSON,
            query_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_city ON queries (city);
            ''')

        connection.commit()

init_db()

def save_query(user_id: int, city: str, weather_data: dict) -> None:
    data = json.dumps(weather_data, ensure_ascii=False)
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO queries (user_id, city, weather_data) VALUES (?, ?, ?)', (user_id, city, data))


def get_queries(user_id: int) -> list[tuple]:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT city, weather_data, datetime(query_date, "localtime") FROM queries WHERE user_id = ? ORDER BY query_date DESC LIMIT 10', (user_id,))
        rows = cursor.fetchall()
        return rows
    
def get_queries_count(user_id: int) -> int:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM queries WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        return total

def clear_queries(user_id: int) -> None:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM queries WHERE user_id = ?', (user_id,))

def get_top_cities(user_id: int, limit: int = 3) -> list[tuple[str, int]]:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT city, COUNT(*) as cnt
            FROM queries
            WHERE user_id = ?
            GROUP BY city
            ORDER BY cnt DESC
            LIMIT ?''', (user_id, limit))
        rows = cursor.fetchall()
        return rows