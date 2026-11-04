# Weather MCP server

A small [MCP](https://modelcontextprotocol.io) server built with FastMCP. It exposes one tool, `get_forecast`, which returns the next five forecast periods for a latitude and longitude from the US National Weather Service API.

> NWS only covers US locations. Requests for other countries return an error message.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Run it

```bash
uv sync
uv run weather.py
```

The server talks over stdio, so it waits silently for an MCP client.

## Add it to Claude Code

```bash
claude mcp add weather -- uv --directory /absolute/path/to/MCP-SERVER run weather.py
```

Then ask Claude something like "What's the weather in Tampa?".

## Tool

| Tool | Arguments | Returns |
|---|---|---|
| `get_forecast` | `latitude: float`, `longitude: float` | Text forecast for the next 5 periods (temperature, wind, conditions) |
