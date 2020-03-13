# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

"""
stocktwits API library
"""
__version__ = '0.0.1'
__author__ = 'John Patrick Roach'
__license__ = 'MIT'

from rug.stocktwits.api import API
from rug.stocktwits.auth import WebAppAuthHandler
from rug.stocktwits.cursor import Cursor
from rug.stocktwits.error import RateLimitError, StocktwitError
from rug.stocktwits.streaming import Stream, StreamListener

# Global, unauthenticated instance of API
api = API()