from dotenv import load_dotenv, find_dotenv
import httpx
import os

load_dotenv(find_dotenv())

FASTAPI_URL = os.getenv('FASTAPI_URL')

def fetch_weather(city: str, forecast: str, part: str) -> dict:
    response =  httpx.get(f'{FASTAPI_URL}/weather/{city}?forecast={forecast}&part={part}')
    data = response.json()
    return data

def fetch_history(user_id: int) -> dict:
    response =  httpx.get(f'{FASTAPI_URL}/history/{user_id}')
    data = response.json()
    return data

def fetch_stats(user_id: int) -> dict:
    response =  httpx.get(f'{FASTAPI_URL}/stats/{user_id}')
    data = response.json()
    return data

def save_history(user_id: int, city: str, weather: dict) -> bool:
    data = {
        'user_id': user_id,
        'city': city,
        'weather': weather
    }
    response =  httpx.post(f'{FASTAPI_URL}/history', json=data)
    return True if response.is_success else False

def delete_history(user_id: int) -> bool:
    response =  httpx.delete(f'{FASTAPI_URL}/history/{user_id}')
    return True if response.is_success else False