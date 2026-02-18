async def run(location: str, unit: str = "celsius") -> str:
    """Fetch weather (mocked for now)."""
    # In a real app, we'd call an API like OpenWeatherMap
    temp = 22 if unit == "celsius" else 72
    condition = "Sunny"
    
    if len(location) % 3 == 0:
        condition = "Cloudy"
        temp -= 5
    elif len(location) % 2 == 0:
        condition = "Partly Cloudy"
        temp += 3

    return f"The current weather in {location} is {temp}°{unit[0].upper()} with {condition} conditions."
