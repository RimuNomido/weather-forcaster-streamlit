from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .forecaster import get_coords, send_request
from .utils import parse_json, display_all_history, parse_weather, parse_query_to_story, parse_stats, WeatherData
from .db import init_db, init_pool, get_queries, save_query, clear_queries, get_queries_count, get_top_cities, close_pool
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import json
import os

load_dotenv(find_dotenv())

YANDEX_URL = 'https://api.weather.yandex.ru/graphql/query'
YANDEX_ACCESS_KEY = os.getenv('YANDEX_ACCESS_KEY')

if not YANDEX_ACCESS_KEY:
    raise ValueError('YANDEX_ACCESS KEY не найден.')

weather_cache = {}
CACHE_TTL = timedelta(minutes=5)

class QueryData(BaseModel):
    user_id: int
    city: str
    weather: dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    await init_db()
    yield
    await close_pool()

app = FastAPI(lifespan=lifespan)

@app.get('/weather/{city}')
async def get_weather(city: str, forecast: str = 'today', part: str = 'day') -> dict:
    if (city, forecast, part) in weather_cache:
        cached_time, cached_data = weather_cache[(city, forecast, part)]
        if datetime.now() - cached_time < CACHE_TTL:
            return cached_data
        else:
            del weather_cache[(city, forecast, part)]

    coords = get_coords(city)
    if coords is None:
        raise HTTPException(status_code=404, detail='Город не найден')
    
    data = await send_request(YANDEX_URL, YANDEX_ACCESS_KEY, coords, forecast, part)
    if data is None:
        raise HTTPException(status_code=503, detail='Ошибка API')
    
    weather = parse_json(data, forecast, part)
    if weather is None:
        raise HTTPException(status_code=500, detail='Ошибка парсинга')
    
    response_data = {
        'city': city,
        'weather': parse_weather(weather, city),
        'row': weather
    }

    weather_cache[(city, forecast, part)] = (datetime.now(), response_data)
    
    return response_data

@app.post('/history')
async def save_query_to_history(query_data: QueryData) -> dict:
    await save_query(query_data.user_id, query_data.city, query_data.weather)
    return {'status': 'ok'}

@app.get('/history/{user_id}')
async def get_history(user_id: int):  
    queries = await get_queries(user_id)
    count = await get_queries_count(user_id)
    queries_to_display_count = len(queries)
    answers_data = []
    for city, data_json, query_date in queries:
        data_dict = json.loads(data_json)
        adapted_date = query_date[:19]
        answer = parse_query_to_story(WeatherData(**data_dict), adapted_date, city)
        answers_data.append(answer)

    return {
        'total': count,
        'total_to_display': queries_to_display_count,
        'history': display_all_history(answers_data, queries_to_display_count)
    }

@app.delete('/history/{user_id}')
async def delete_history(user_id: int) -> dict:
    await clear_queries(user_id)
    return {'status' : 'ok'}

@app.get('/stats/{user_id}')
async def get_stats(user_id: int) -> dict:
    total = await get_queries_count(user_id)
    stats = await get_top_cities(user_id)
    top_cities = [{'city': city, 'count': cnt} for city, cnt in stats]
    parsed_top_cities = parse_stats(total, top_cities)
    return {
        'total_queries': total,
        'top_cities': top_cities,
        'stats': parsed_top_cities
    }