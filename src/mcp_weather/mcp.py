import os

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .components.weather import WeatherComponent
from .providers import OpenWeather, WeatherProvider


class MCPWeather:
    server: FastMCP[None]
    weather_component: WeatherComponent

    @staticmethod
    def from_env() -> 'MCPWeather':
        provider_name = os.environ.get('WEATHER_PROVIDER')

        if not provider_name:
            raise ValueError('Missing WEATHER_PROVIDER env var')

        match provider_name.lower():
            case 'openweather':
                return MCPWeather(OpenWeather.from_env())
            case _:
                raise ValueError(f'Unsupported WEATHER_PROVIDER: {provider_name}')

    def __init__(self, provider: WeatherProvider) -> None:
        self.server = FastMCP(
            name='mcp-weather',
            dependencies=['aiohttp[speedups]'],
        )

        self.weather_component = WeatherComponent(provider=provider)

    def register_all(self) -> None:
        self.weather_component.register_all(mcp_server=self.server)  # pyright: ignore[reportUnknownMemberType]
        self.server.custom_route('/health', methods=['GET'])(self._health)

    def run(self, **kwargs: object):
        self.server.run(**kwargs)  # pyright: ignore[reportArgumentType]

    async def _health(self, _request: Request) -> PlainTextResponse:
        return PlainTextResponse('OK')
