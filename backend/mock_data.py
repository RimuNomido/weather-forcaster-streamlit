# backend/mock_data.py

MOCK_WEATHER_RESPONSE = {
    "data": {
        "weatherByPoint": {
            "now": {
                "cloudiness": "CLEAR",
                "humidity": 65,
                "precType": "NO_TYPE",
                "precStrength": "ZERO",
                "pressure": 1012,
                "temperature": 22,
                "fahrenheit": 72,
                "windSpeed": 3.5,
                "windDirection": "NORTH"
            }
        }
    }
}

# Можно добавить несколько городов
MOCK_CITIES = {
    "москва": MOCK_WEATHER_RESPONSE,
    "тюмень": {
        "data": {
            "weatherByPoint": {
                "now": {
                    "cloudiness": "CLOUDY",
                    "humidity": 80,
                    "precType": "RAIN",
                    "precStrength": "AVERAGE",
                    "pressure": 1005,
                    "temperature": 12,
                    "fahrenheit": 54,
                    "windSpeed": 7.2,
                    "windDirection": "SOUTH_WEST"
                }
            }
        }
    }
    # Добавьте другие города по желанию
}