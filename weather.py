import requests


LATITUDE = 1.3521
LONGITUDE = 103.8198

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()

def format_current_weather(weather):

    current = weather["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    feels_like = current["apparent_temperature"]
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]

    description = get_weather_description(weather_code)

    return (
        f"🌤️ Current Weather\n\n"
        f"{description}\n"
        f"🌡️ Temperature: {temperature}°C\n"
        f"🥵 Feels like: {feels_like}°C\n"
        f"💧 Humidity: {humidity}%\n"
        f"💨 Wind: {wind_speed} km/h"
    )

def get_weather_description(code):

    descriptions = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Depositing rime fog",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        61: "🌦️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        80: "🌦️ Rain showers",
        81: "🌧️ Moderate rain showers",
        82: "⛈️ Violent rain showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with hail",
        99: "⛈️ Thunderstorm with heavy hail"
    }

    return descriptions.get(code, "🌤️ Unknown conditions")

def create_report(weather):

    daily = weather["daily"]

    date = daily["time"][0]

    min_temp = daily["temperature_2m_min"][0]
    max_temp = daily["temperature_2m_max"][0]

    rain_probability = (
        daily["precipitation_probability_max"][0]
    )

    rainfall = daily["precipitation_sum"][0]

    can_cycle = rain_probability < 30 and rainfall == 0
    cycling_advice = "Yes" if can_cycle else "No"

    return f"""🌤️ Singapore Weather

📅 {date}

🌡️ {min_temp}°C – {max_temp}°C

🌧️ Rain probability: {rain_probability}%

💧 Expected rainfall: {rainfall} mm

🚲 Cycle: {cycling_advice}
"""