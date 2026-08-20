import requests


LATITUDE = 1.3521
LONGITUDE = 103.8198


def get_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum"
        ],
        "timezone": "Asia/Singapore"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()

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