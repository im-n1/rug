import time
from datetime import date, timedelta

from . import BaseAPI


class UnofficialAPI(BaseAPI):
    def get_earnings_calendar(self, from_date, to_date):
        """
        Fetches upcomming earnings annoucements within
        the given date range.
        Maximum date span is 14 days.

        Each earning dict has the following structure:

        * date
        * symbol
        * time
        * when (BEFORE_OPEN or AFTER_CLOSE)

        :param date from_date: Beginning of the calendar span.
        :param date end_date: End of the calendar span.
        :return: List of earning objects.
        :rtype: list
        """

        # Check params.
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise AttributeError(
                'Both "from_date" and "to_date" params'
                "need to be datetime.date instances."
            )

        # Check date span.
        if 14 < (to_date - from_date).days:
            raise ValueError("Maximum date span is 14 days.")

        response = self._get(
            "https://api.stocktwits.com/api/2/discover/earnings_calendar?"
            f"date_from={from_date}&date_to={to_date}"
        )
        earnings = response.json()["earnings"]
        data = []

        for _, item in earnings.items():
            for stock in item["stocks"]:
                data.append(
                    {
                        "date": date(*time.strptime(stock["date"], "%Y-%m-%d")[:3]),
                        "symbol": stock["symbol"],
                        "time": time.strptime(stock["time"], "%H:%M:%S"),
                        "when": "BEFORE_OPEN"
                        if "08:00:00" == stock["time"]
                        else "AFTER_CLOSE",
                    }
                )

        return data
