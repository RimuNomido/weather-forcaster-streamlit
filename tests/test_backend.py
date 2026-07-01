from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
import json

client = TestClient(app)

def test_weather_endpoint():
    fake_response = {'data': {'weatherByPoint': {'now': {'cloudiness': 'CLEAR', 'humidity': 64, 'precType': 'NO_TYPE', 'precStrength': 'ZERO', 'pressure': 746, 'temperature': 21, 'fahrenheit': 69, 'windSpeed': 0.8, 'windDirection': 'NORTH'}}}}
    with patch("backend.app.main.send_request") as mock_send_request:
        mock_send_request.return_value = fake_response
        response = client.get('/weather/Тюмень?forecast=now&part=day')

        assert response.status_code == 200
        assert response.json() == {"city": "Тюмень",
                                    "weather": {
                                        "Город": "Тюмень 🏙️",
                                        "Облачность": "☀️ Ясно",
                                        "Влажность": "💧 64%",
                                        "Тип осадков": "🚫 Нет осадков",
                                        "Интенсивность осадков": "🛑 Отсутствует",
                                        "Атмосферное давление": "🧭 746 мм рт. ст.",
                                        "Температура": "🌡️ 21 °C / 69 °F",
                                        "Скорость ветра": "🍃 0.8 м/с",
                                        "Направление ветра": "⬆️ Север"
                                    },
                                    "row": {
                                    "cloudiness": "CLEAR",
                                    "humidity": 64,
                                    "precType": "NO_TYPE",
                                    "precStrength": "ZERO",
                                    "pressure": 746,
                                    "temperature": 21,
                                    "fahrenheit": 69,
                                    "windSpeed": 0.8,
                                    "windDirection": "NORTH"
                                }}

def test_history_endpoint():
    expected = {
                "total": 2,
                "total_to_display": 2,
                "history": "🗓️ Дата: 2026-07-01 05:12:44\n\n\n        Город: Тюмень 🏙️\n\n        Облачность: ☁️ Пасмурно\n\n        Влажность: 💧 51%\n\n        Тип осадков: 🚫 Нет осадков\n\n        Интенсивность осадков: 🛑 Отсутствует\n\n        Атмосферное давление: 🧭 743 мм рт. ст.\n\n        Температура: 🌡️ 22 °C / 71 °F\n\n        Скорость ветра: 💨 3 м/с\n\n        Направление ветра: ↙️ Юго-запад\n🗓️ Дата: 2026-06-30 21:02:00\n\n\n        Город: Тюмень 🏙️\n\n        Облачность: ☁️ Пасмурно\n\n        Влажность: 💧 51%\n\n        Тип осадков: 🚫 Нет осадков\n\n        Интенсивность осадков: 🛑 Отсутствует\n\n        Атмосферное давление: 🧭 743 мм рт. ст.\n\n        Температура: 🌡️ 22 °C / 71 °F\n\n        Скорость ветра: 💨 3 м/с\n\n        Направление ветра: ↙️ Юго-запад\n"
                }
    fake_response = [
        (
            "Тюмень",
            json.dumps({
                "cloudiness": "OVERCAST",
                "humidity": 51,
                "precType": "NO_TYPE",
                "precStrength": "ZERO",
                "pressure": 743,
                "temperature": 22,
                "fahrenheit": 71,
                "windSpeed": 3,
                "windDirection": "SOUTH_WEST"
            }),
            "2026-07-01 05:12:44.500073+05"
        ),
        (
            "Тюмень",
            json.dumps({
                "cloudiness": "OVERCAST",
                "humidity": 51,
                "precType": "NO_TYPE",
                "precStrength": "ZERO",
                "pressure": 743,
                "temperature": 22,
                "fahrenheit": 71,
                "windSpeed": 3,
                "windDirection": "SOUTH_WEST"
            }),
            "2026-06-30 21:02:00.090127+05"
        )
    ]
    with patch('backend.app.main.get_queries') as mock_get_queries, \
        patch('backend.app.main.get_queries_count') as mock_get_queries_count:
        mock_get_queries.return_value = fake_response
        mock_get_queries_count.return_value = 2
        response = client.get('/history/3')
        assert response.status_code == 200
        assert response.json() == expected

def test_stats_endpoint():
    expected = {
                "total_queries": 11,
                "top_cities": [
                    {
                    "city": "Санкт-Петербург",
                    "count": 6
                    },
                    {
                    "city": "Тюмень",
                    "count": 5
                    }
                ],
                "stats": "Всего запросов: 11\nЧаще всего вы искали погоду в:\n- Санкт-Петербург: 6 раз\n- Тюмень: 5 раз\n"
                }
    fake_response = [
    ("Санкт-Петербург", 6),
    ("Тюмень", 5)
    ]
    with patch('backend.app.main.get_top_cities') as mock_get_top_cities, \
        patch('backend.app.main.get_queries_count') as mock_get_queries_count:
        mock_get_top_cities.return_value = fake_response
        mock_get_queries_count.return_value = 11
        response = client.get('/stats/12345')
        assert response.status_code == 200
        assert response.json() == expected
