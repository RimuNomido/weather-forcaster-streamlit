from geopy import Nominatim
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

coords_cache = {}

http_client = httpx.AsyncClient(timeout=5, limits=httpx.Limits(max_keepalive_connections=5))

def get_coords(city, ) -> tuple[float, float] | None:
    if city in coords_cache:
        return coords_cache[city]
    
    geolocator = Nominatim(user_agent='vladimir_safronov')
    loc = geolocator.geocode(city)

    if loc is None:
        return None

    coords = (loc.latitude, loc.longitude)
    coords_cache[city] = coords
    return coords

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=3))
async def send_request(url, access_key, coords: tuple[float, float]) -> dict | None:
    headers = {'X-Yandex-Weather-Key': access_key}
    query = """
    query GetWeather($lat: Float!, $lon: Float!) {
        weatherByPoint(request: { lat: $lat, lon: $lon }) {
            now {
            cloudiness
            humidity
            precType
            precStrength
            pressure
            temperature
            fahrenheit: temperature(unit: FAHRENHEIT)
            windSpeed
            windDirection
            }
        }
    }
    """
    variables = {
        "lat": coords[0],
        "lon": coords[1]
    }

    try:
        response = await http_client.post(url, headers=headers, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        return None
    except ValueError as e:
        return None