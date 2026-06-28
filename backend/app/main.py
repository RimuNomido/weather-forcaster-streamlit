from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .forecaster import get_coords, send_request
from .utils import parse_json, display_all_history, parse_weather, parse_query_to_story, parse_stats, WeatherData
from .db import get_queries, save_query, clear_queries, get_queries_count, get_top_cities
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import json
import os

load_dotenv(find_dotenv())

YANDEX_URL = 'https://api.weather.yandex.ru/graphql/query'
YANDEX_ACCESS_KEY = os.getenv('access_key')

if not YANDEX_ACCESS_KEY:
    raise ValueError('YANDEX_ACCESS KEY не найден.')

app = FastAPI()

weather_cache = {}
CACHE_TTL = timedelta(minutes=5)

class QueryData(BaseModel):
    user_id: int
    city: str
    weather: dict

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
def save_query_to_history(query_data: QueryData) -> dict:
    save_query(query_data.user_id, query_data.city, query_data.weather)
    return {'status': 'ok'}

@app.get('/history/{user_id}')
def get_history(user_id: int):  
    queries = get_queries(user_id)
    count = get_queries_count(user_id)
    queries_to_display_count = len(queries)
    answers_data = []
    for city, data_json, query_date in queries:
        data_dict = json.loads(data_json)
        answer = parse_query_to_story(WeatherData(**data_dict), query_date, city)
        answers_data.append(answer)

    return {
        'total': count,
        'total_to_display': queries_to_display_count,
        'history': display_all_history(answers_data, queries_to_display_count)
    }

@app.delete('/history/{user_id}')
def delete_history(user_id: int) -> dict:
    clear_queries(user_id)
    return {'status' : 'ok'}

@app.get('/stats/{user_id}')
def get_stats(user_id: int) -> dict:
    total = get_queries_count(user_id)
    stats = get_top_cities(user_id)
    top_cities = [{'city': city, 'count': cnt} for city, cnt in stats]
    parsed_top_cities = parse_stats(total, top_cities)
    return {
        'total_queries': total,
        'top_cities': top_cities,
        'stats': parsed_top_cities
    }