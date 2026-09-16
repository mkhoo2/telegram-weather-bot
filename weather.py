import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# NEA / data.gov.sg real-time weather APIs
TWO_HOUR_URL = "https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast"
TWENTY_FOUR_HOUR_URL = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"
PSI_URL = "https://api-open.data.gov.sg/v2/real-time/api/psi"
PM25_URL = "https://api-open.data.gov.sg/v2/real-time/api/pm25"

TIMEOUT = 10
SINGAPORE_TZ = ZoneInfo("Asia/Singapore")

# Representative NEA forecast areas for the four regions.
# The 2-hour API gives area-level forecasts, while the 24-hour API
# already provides regional forecasts (north/east/south/west).
REGION_AREAS = {
    "West": [
        "Boon Lay", "Bukit Batok", "Bukit Panjang", "Bukit Timah",
        "Choa Chu Kang", "Clementi", "Jalan Bahar", "Jurong East",
        "Jurong Island", "Jurong West", "Pioneer", "Tengah", "Tuas",
        "Western Islands", "Western Water Catchment", "Sungei Kadut",
    ],
    "East": [
        "Bedok", "Changi", "Geylang", "Hougang", "Marine Parade",
        "Pasir Ris", "Paya Lebar", "Pulau Tekong", "Pulau Ubin",
        "Punggol", "Seletar", "Sengkang", "Tampines", "Serangoon",
    ],
    "North": [
        "Ang Mo Kio", "Bishan", "Central Water Catchment", "Lim Chu Kang",
        "Mandai", "Sembawang", "Woodlands", "Yishun", "Choa Chu Kang",
        "Bukit Panjang", "Sungei Kadut",
    ],
    "South": [
        "Bukit Merah", "City", "Kallang", "Queenstown", "Sentosa",
        "Southern Islands", "Tanglin", "Novena",
    ],
}


def _get_json(url):
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    if payload.get("code") != 0:
        raise RuntimeError(payload.get("errorMsg") or "NEA API returned an error")

    return payload["data"]


def get_2hour_weather():
    """Return the latest NEA 2-hour forecast."""
    return _get_json(TWO_HOUR_URL)


def get_24hour_weather():
    """Return the latest NEA 24-hour forecast."""
    return _get_json(TWENTY_FOUR_HOUR_URL)


def get_psi_weather():
    """Return the latest NEA PSI update."""
    return _get_json(PSI_URL)


def get_pm25_weather():
    """Return the latest NEA 1-hour PM2.5 update."""
    return _get_json(PM25_URL)


def _region_from_area(area):
    for region, areas in REGION_AREAS.items():
        if area in areas:
            return region
    return None


def _summarize_2hour(data):
    """Convert the 47 NEA area forecasts into one forecast per region."""
    items = data.get("items", [])
    if not items:
        return {}

    latest = items[-1]
    forecasts = latest.get("forecasts", [])

    grouped = {region: [] for region in REGION_AREAS}

    for item in forecasts:
        region = _region_from_area(item.get("area"))
        if region:
            grouped[region].append(item.get("forecast", "Unknown"))

    result = {}
    for region, values in grouped.items():
        if not values:
            result[region] = "Unavailable"
            continue

        # Most common forecast in the region.
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        result[region] = max(counts, key=counts.get)

    return {
        "timestamp": latest.get("timestamp"),
        "update_timestamp": latest.get("update_timestamp"),
        "valid_period": latest.get("valid_period", {}),
        "regions": result,
    }


def _get_latest_24hour_record(data):
    records = data.get("records", [])
    if not records:
        raise RuntimeError("NEA 24-hour forecast returned no records")
    return records[-1]


def _psi_status(value):
    if value is None:
        return "Unavailable"
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 200:
        return "Unhealthy"
    if value <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def _summarize_psi(data):
    """Extract the regional 24-hour PSI values with per-region status."""
    items = data.get("items", [])
    if not items:
        return {
            "timestamp": None,
            "updated_timestamp": None,
            "regions": {},
        }

    latest = items[-1]
    readings = latest.get("readings", {})
    psi = readings.get("psi_twenty_four_hourly", {})

    regions = {
        region.title(): {
            "value": value,
            "status": _psi_status(value),
        }
        for region, value in psi.items()
    }

    return {
        "timestamp": latest.get("timestamp"),
        "updated_timestamp": latest.get("updatedTimestamp"),
        "regions": regions,
    }


def _pm25_status(value):
    if value is None:
        return "Unavailable"
    if value <= 55:
        return "Normal"
    if value <= 150:
        return "Elevated"
    if value <= 250:
        return "High"
    return "Very High"


def _summarize_pm25(data):
    """Extract the regional 1-hour PM2.5 readings with status."""
    items = data.get("items", [])
    if not items:
        return {
            "timestamp": None,
            "updated_timestamp": None,
            "regions": {},
        }

    latest = items[-1]
    readings = latest.get("readings", {})
    pm25 = readings.get("pm25_one_hourly", {})

    regions = {
        region.title(): {
            "value": value,
            "status": _pm25_status(value),
        }
        for region, value in pm25.items()
    }

    return {
        "timestamp": latest.get("timestamp"),
        "updated_timestamp": latest.get("updatedTimestamp"),
        "regions": regions,
    }


def _summarize_24hour(data):
    """Extract the regional 24-hour forecast and time periods."""
    record = _get_latest_24hour_record(data)

    periods = []
    for period in record.get("periods", []):
        regions = period.get("regions", {})
        periods.append({
            "text": period.get("timePeriod", {}).get("text", ""),
            "start": period.get("timePeriod", {}).get("start"),
            "end": period.get("timePeriod", {}).get("end"),
            "regions": {
                region.title(): regions.get(region, {}).get("text", "Unavailable")
                for region in ("west", "east", "north", "south")
            },
        })

    return {
        "date": record.get("date"),
        "timestamp": record.get("timestamp"),
        "updated_timestamp": record.get("updatedTimestamp"),
        "valid_period": record.get("general", {}).get("validPeriod", {}),
        "temperature": record.get("general", {}).get("temperature", {}),
        "humidity": record.get("general", {}).get("relativeHumidity", {}),
        "wind": record.get("general", {}).get("wind", {}),
        "general_forecast": record.get("general", {}).get("forecast", {}).get("text"),
        "periods": periods,
    }


def get_singapore_weather():
    """Fetch and combine NEA's weather and air quality updates."""
    two_hour = _summarize_2hour(get_2hour_weather())
    twenty_four_hour = _summarize_24hour(get_24hour_weather())
    psi = _summarize_psi(get_psi_weather())
    pm25 = _summarize_pm25(get_pm25_weather())

    return {
        "two_hour": two_hour,
        "twenty_four_hour": twenty_four_hour,
        "psi": psi,
        "pm25": pm25,
    }


def _weather_icon(text):
    text = text.lower()

    if "thunder" in text:
        return "⛈️"
    if "rain" in text or "shower" in text or "drizzle" in text:
        return "🌧️"
    if "cloud" in text or "overcast" in text:
        return "☁️"
    if "fair" in text or "clear" in text:
        return "☀️"
    if "wind" in text:
        return "💨"
    if "fog" in text:
        return "🌫️"

    return "🌤️"


def _format_region_line(region, forecast):
    return f"{_weather_icon(forecast)} {region}: {forecast}"


def format_singapore_weather(weather):
    """Format the combined forecast for Telegram."""
    two_hour = weather["two_hour"]
    twenty_four = weather["twenty_four_hour"]
    psi = weather.get("psi", {})

    valid_text = two_hour.get("valid_period", {}).get("text", "Next 2 hours")
    updated = two_hour.get("update_timestamp")

    lines = [
        "🇸🇬 Singapore Weather",
        "",
        f"🕐 2-hour forecast: {valid_text}",
    ]

    if updated:
        try:
            dt = datetime.fromisoformat(updated).astimezone(SINGAPORE_TZ)
            lines.append(f"Updated: {dt.strftime('%d %b %Y, %I:%M %p')}")
        except ValueError:
            pass

    lines.extend(["", "🌦️ NEXT 2 HOURS"])

    for region in ("West", "East", "North", "South"):
        forecast = two_hour.get("regions", {}).get(region, "Unavailable")
        lines.append(_format_region_line(region, forecast))

    lines.extend(["", "📅 NEXT 24 HOURS"])

    for period in twenty_four.get("periods", []):
        lines.append("")
        lines.append(f"🕐 {period['text']}")

        for region in ("West", "East", "North", "South"):
            forecast = period["regions"].get(region, "Unavailable")
            lines.append(_format_region_line(region, forecast))

    temperature = twenty_four.get("temperature", {})
    if temperature:
        low = temperature.get("low")
        high = temperature.get("high")
        if low is not None and high is not None:
            lines.extend(["", f"🌡️ Temperature: {low}°C – {high}°C"])

    humidity = twenty_four.get("humidity", {})
    if humidity:
        low = humidity.get("low")
        high = humidity.get("high")
        if low is not None and high is not None:
            lines.append(f"💧 Humidity: {low}% – {high}%")

    wind = twenty_four.get("wind", {})
    speed = wind.get("speed", {})
    direction = wind.get("direction")
    if speed:
        low = speed.get("low")
        high = speed.get("high")
        if low is not None and high is not None:
            wind_text = f"💨 Wind: {low}–{high} km/h"
            if direction:
                wind_text += f", {direction}"
            lines.append(wind_text)

    psi_regions = psi.get("regions", {})
    if psi_regions:
        lines.extend(["", "🌫️ PSI (24-hr)"])
        for region in ("North", "South", "East", "West", "Central"):
            region_data = psi_regions.get(region)
            if not region_data:
                continue
            value = region_data.get("value", "Unavailable")
            status = region_data.get("status", "Unavailable")
            lines.append(f"{region}: {value} ({status})")

    pm25 = weather.get("pm25", {})
    pm25_regions = pm25.get("regions", {})
    if pm25_regions:
        lines.extend(["", "🌫️ PM2.5 (1-hr, µg/m3)"])
        for region in ("North", "South", "East", "West", "Central"):
            region_data = pm25_regions.get(region)
            if not region_data:
                continue
            value = region_data.get("value", "Unavailable")
            status = region_data.get("status", "Unavailable")
            lines.append(f"{region}: {value} ({status})")

    return "\n".join(lines)


# Backwards-compatible aliases for any other code that may still import these.
def get_weather(latitude=None, longitude=None):
    return get_singapore_weather()


def format_current_weather(weather):
    return format_singapore_weather(weather)
