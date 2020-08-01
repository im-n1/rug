import httpx

from .exceptions import HttpException


class BaseAPI:

    timeout = 10

    def __init__(self, symbol=None):
        """
        Constructor.

        :param str symbol: Symbol of te item we wanna get info about.
        """

        if symbol:
            self.symbol = str(symbol)

    def _get(self, *args):
        """
        TBD
        """

        try:
            return httpx.get(*args, timeout=self.timeout)
        except Exception as exc:
            raise HttpException(
                f"Couldn't perform GET request with args {args}"
            ) from exc

    async def _aget(self, *args):

        async with httpx.AsyncClient() as client:

            try:
                return await client.get(*args, timeout=self.timeout)
            except Exception as exc:
                raise HttpException(
                    f"Couldn't perform GET request with args {args}"
                ) from exc
