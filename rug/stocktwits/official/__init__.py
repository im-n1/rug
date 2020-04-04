# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

"""
stocktwits API library
"""
__version__ = '0.0.1'
__author__ = 'John Patrick Roach'
__license__ = 'MIT'

from rug.stocktwits.official.api import API
from rug.stocktwits.official.auth import WebAppAuthHandler
from rug.stocktwits.official.cursor import Cursor
from rug.stocktwits.official.error import RateLimitError, StocktwitError
from rug.stocktwits.official.models import Message, Symbol, ModelFactory, SearchResults, Watchlist, User
from rug.stocktwits.official.streaming import Stream, StreamListener

# Global, unauthenticated instance of API
api = API()