# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

import six


class StocktwitError(Exception):
    """stocktwits exception"""

    def __init__(self, reason, response=None, api_code=None):
        self.reason = six.text_type(reason)
        self.response = response
        self.api_code = api_code
        super(StocktwitError, self).__init__(reason)

    def __str__(self):
        return self.reason


def is_rate_limit_error_message(message):
    """Check if the supplied error message belongs to a rate limit error."""
    return isinstance(message, list) \
        and len(message) > 0 \
        and 'code' in message[0] \
        and message[0]['code'] == 88


class RateLimitError(StocktwitError):
    """Exception for Tweepy hitting the rate limit."""
    # RateLimitError has the exact same properties and inner workings
    # as StocktwitError for backwards compatibility reasons.
    pass
