from typing import Any
import asyncio
import logging
import sys

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

# Log to stderr: with the stdio transport, stdout carries the MCP protocol
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# constants
NWS_API_URL = "https://api.weather.gov"
USER_AGENT = "MCP-Server-POC/0.1.0"


# helper function to fetch weather data from NWS API
async def fetch_weather_data(url: str) -> dict[str, Any] | None:
    """
    Fetch weather data from NWS API

    @param url: URL to fetch weather data from
    @return: Weather data if successful, None otherwise
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error("Error fetching weather data from NWS API: %s", e)
        return None

    except httpx.RequestError as e:
        logger.error("Error making request to NWS API: %s", e)
        return None

    except ValueError as e:
        logger.error("Invalid JSON returned by NWS API: %s", e)
        return None


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get the weather forecast for a US location using the National Weather Service API.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    Returns:
        Text forecast for the next 5 periods (temperature, wind, conditions),
        or an error message if the location is outside the US or the API fails.
    """
    # First get the forecast grid endpoint (NWS accepts at most 4 decimals)
    points_url = f"{NWS_API_URL}/points/{latitude:.4f},{longitude:.4f}"
    points_data = await fetch_weather_data(points_url)

    forecast_url = (points_data or {}).get("properties", {}).get("forecast")
    if not forecast_url:
        return "Unable to fetch forecast data for this location"

    forecast_data = await fetch_weather_data(forecast_url)
    if not forecast_data:
        return "Unable to fetch detailed forecast data for this location"

    periods = forecast_data.get("properties", {}).get("periods") or []
    if not periods:
        return "No forecast periods available"

    # Format the next 5 periods into a readable forecast
    forecasts = []
    for period in periods[:5]:
        forecasts.append(
            f"{period.get('name', 'Unknown period')}:\n"
            f"Temperature: {period.get('temperature')}°{period.get('temperatureUnit', '')}\n"
            f"Wind: {period.get('windSpeed', '')} {period.get('windDirection', '')}\n"
            f"Forecast: {period.get('detailedForecast', '')}"
        )

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Running as a script: print the forecast for New York City (40.7128, -74.0060)
        print(asyncio.run(get_forecast(latitude=40.7128, longitude=-74.0060)))
        # Running as a script: print the forecast for Los Angeles (34.0522, -118.2437)
        print(asyncio.run(get_forecast(latitude=34.0522, longitude=-118.2437)))
    else:
        # Run the MCP server
        mcp.run(transport="stdio")
