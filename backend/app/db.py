from dotenv import load_dotenv, find_dotenv
import functools
import os
import asyncpg
import json

load_dotenv(find_dotenv())
user = os.getenv('db_user')
passwd = os.getenv('db_pass')
pool = None

def handle_db_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncpg.UniqueViolationError:
            print(' Ошибка: Такие данные уже существуют')
            return None
        except asyncpg.PostgresConnectionError:
            print('Ошибка: Нет соединения с базой данных')
            return None
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            return None
    return wrapper

@handle_db_errors
async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
    host='localhost',
    database='queries',
    user=user,
    password=passwd,
    min_size=1,
    max_size=10
    )

@handle_db_errors
async def init_db():
    async with pool.acquire() as conn:

        await conn.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            user_id INTEGER,
            city TEXT NOT NULL,
            weather_data jsonb NOT NULL DEFAULT '{}'::jsonb,
            query_date TIMESTAMPTZ DEFAULT NOW()
            );
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_city ON queries (city);
            ''')

@handle_db_errors
async def close_pool():
    await pool.close()

@handle_db_errors
async def save_query(user_id: int, city: str, weather_data: dict) -> None:
    async with pool.acquire() as conn:
        data = json.dumps(weather_data, ensure_ascii=False)
        await conn.execute('INSERT INTO queries (user_id, city, weather_data) VALUES ($1, $2, $3);', user_id, city, data)

@handle_db_errors
async def get_queries(user_id: int) -> list[tuple]:
    query = 'SELECT city, weather_data, query_date FROM queries WHERE user_id = $1 ORDER BY query_date DESC LIMIT 10;'
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, user_id)
        return rows
    
@handle_db_errors
async def get_queries_count(user_id: int) -> int:
    query = 'SELECT COUNT(*) FROM queries WHERE user_id = $1;'
    async with pool.acquire() as conn:
        total = await conn.fetchval(query, user_id)
        return total

@handle_db_errors
async def clear_queries(user_id: int) -> None:
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM queries WHERE user_id = $1;', user_id)

@handle_db_errors
async def get_top_cities(user_id: int, limit: int = 3) -> list[tuple[str, int]]:
    query = '''
            SELECT city, COUNT(*) as cnt
            FROM queries
            WHERE user_id = $1
            GROUP BY city
            ORDER BY cnt DESC
            LIMIT $2;
            '''
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, user_id, limit)
        return rows