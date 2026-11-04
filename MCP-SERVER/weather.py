from typing import Any, Union
import httpx
from mcp.server.fastmcp import FastMCP
import asyncio
import json

mcp = FastMCP("weather")

# constants
NWS_API_URL = "https://api.weather.gov"
USER_AGENT = "MCP-Server-POC/0.1.0"

#helper function to fetch weather data from NWS API
async def fetch_weather_data(url: str) -> Union[dict[str, Any], None]:
    """
    Fetch weather data from NWS API

    @param url: URL to fetch weather data from
    @return: Weather data if successful, None otherwise
    """ 
    try:

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url = url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"Error fetching weather data from NWS API: {e}")
        return None

    except httpx.RequestError as e:
        print(f"Error making request to NWS API: {e}")
        return None

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str :
    """
    Get current weather for a location given latitude and longitude using NWS API

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    Returns:
        Forecast if successful, None otherwise

    """

    # First get the forecast grid endpoint
    points_url = f"{NWS_API_URL}/points/{latitude},{longitude}"
    points_data = await fetch_weather_data(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location"

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await fetch_weather_data(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast data for this location"


    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []

    for period in periods[:5]: # Only show the next 5 periods
        forecast = f"""

            {period['name']},
            Temperature: {period["temperature"]}*{period["temperatureUnit"]},
            Wind: {period["windSpeed"]} {period["windDirection"]},
            Forecast: {period["detailedForecast"]},
        
        """ 

        forecasts.append(forecast)

    
    # Get the forecast data from the forecast response
    return "\n---\n".join(forecasts)

if __name__ == "__main__":

    """

    Coordinates for New York City: 40.7128, -74.0060

    """

    # runing the program as a script
    # Print the forecast for New York City 
    # print(asyncio.run(get_forecast(latitude=40.7128, longitude=-74.0060)))

    # Run the MCP server
    mcp.run(transport="stdio")


