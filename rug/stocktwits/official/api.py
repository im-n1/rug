# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

import mimetypes
import os
import re

import six
from rug.stocktwits.official.error import StocktwitError
from rug.stocktwits.official.parsers import ModelParser, Parser

from rug.stocktwits.official.binder import bind_api


class API(object):
    """ StockTwits API
    :reference: https://api.stocktwits.com/developers/docs/api
    :rate_limiting: The Stocktwits API only allows clients to make a limited number of calls in a given hour. This
                    policy affects the APIs in different ways.
                    Default API rate limiting:
                    The default rate limit for calls to the API varies depending on the authorization method being used
                    and whether the method itself requires authentication.
                    Unauthenticated calls are permitted 200 requests per hour and measured against the public facing IP
                    of the server or device making the request.
                    Authenticated calls are permitted 400 requests per hour and measured against the access token used
                    in the request.
                    All Stocktwits API responses return a set of rate limit HTTP headers. These headers provide the
                    limit, remaining amount of requests for that limit, and a UNIX timestamp of when the rate limit
                    resets again.
                    X-RateLimit-Limit: 200
                    X-RateLimit-Remaining: 146
                    X-RateLimit-Reset: 1345147112
                    Rate limits and errors:
                    Error responses are rate limited against either the authenticated or unauthenticated rate limit
                    depending on where the error occurs. Unauthenticated responses will typically return a HTTP 400 or
                    401 status code.
                    Rate limits are applied to methods that request information with the HTTP GET or HEAD method.
                    Generally API methods that use HTTP POST to submit data to Stocktwits are not rate limited. Every
                    method in the API documentation displays if it is rate limited or not.
                    Actions such as publishing messages, sending direct messages, following and unfollowing stocks or
                    users are not directly rate limited by the API but are subject to fair use limits.
                    If you are rate limited:
                    If your application is being rate-limited it will receive HTTP 429 response code. It is best
                    practice for applications to monitor their current rate limit status and dynamically throttle
                    requests.
                    Partner API:
                    If your application requires extended data or a higher rate limit, you may want to consider becoming
                    a partner. Please contact our team for more information.
                    Blacklisting:
                    We ask that you honor the rate limits. If you or your application abuses the rate limits we will be
                    forced to suspend and or blacklist it. If you are blacklisted you will be unable to get a response
                    from the Stocktwits API.
                    If you or your application has been blacklisted and you think there has been an error you can
                    contact us via email for support.
    :parameters: Some API methods take optional or required parameters. When making requests with parameters values
                    should be converted to UTF-8 and URL encoded.
                    There is one special parameter in the Stocktwits API:
                    callback: Used only when requesting JSON formatted responses, this parameter wraps your response in
                    a callback method of your choice. For example, appending &callback=myFancyFunction to your request
                    will result in a response body of: myFancyFunction(...). Callbacks may only contain alphanumeric
                    characters and underscores; any invalid characters will be stripped.
                    Where noted, some API methods will return different results based on HTTP headers sent by the
                    client. Where the same behavior can be controlled by both a parameter and an HTTP header, the
                    parameter will take precedence.
    :pagination: Clients may access a theoretical maximum of 800 messages via the cursor parameters for the API methods.
                    Requests for more than the limit will result in a reply with a status code of 200 and an empty
                    result in the format requested. Stocktwits still maintains a database of all the messages sent by a
                    user. However, to ensure performance of the site, this artificial limit is temporarily in place.
                    There are two main parameters when paginating through results.
                    Since will return results with an ID greater than (more recent than) the specified ID. Use this when
                    getting new results or messages to a stream.
                    Max will return results with an ID less than (older than) or equal to the specified ID. Use this to
                    get older results or messages that have previously been published.
    :responses: The Stocktwits API attempts to return appropriate HTTP status codes for every request. The following
                    table describes the codes which may appear when working with the API:
                    200 - Success
                    400 - Bad Request
                    401 - Unauthorized
                    403 - Forbidden
                    404 - Not Found
                    422 - Unprocessable Entity
                    429 - Too Many Requests
                    500 - Internal Server Error
                    503 - Service Unavailable
                    504 - Gateway Timeout
    :error_codes: Error messages contain machine-parseable codes as well as additional descriptive error text. The text
                    for an error message may change, the status codes will stay the same. Errors will look like this:
                    {
                      "response": {
                        "status": 400
                      },
                      "errors": [{
                          "message": "SSL is required for all API requests"
                      }]
                    }
                    {
                      "response": {
                        "status": 401
                      },
                      "errors": [{
                        "message": "Authentication required"
                      }]
                    }
                    {
                      "response": {
                        "status": 401
                      },
                      "errors": [{
                        "message": "Stream required authentication"
                      }]
                    }
                    {
                      "response": {
                        "status": 401
                      },
                      "errors": [{
                        "message": "Account suspended"
                      }]
                    }
                    {
                      "response": {
                        "status": 422
                      },
                      "errors": [{
                        "message": "Duplicate messages within 30 minutes will not be posted."
                      }]
                    }
                    {
                      "response": {
                        "status": 422
                      },
                      "errors": [{
                        "message": "Body can't be blank"
                      }]
                    }
                    {
                      "response": {
                        "status": 422
                      },
                      "errors": [{
                        "message": "You can't like your own messages."
                      }]
                    }
                    {
                      "response": {
                        "status": 429
                      },
                      "errors": [{
                        "message": "Rate limit exceeded. Client may not make more than N requests an hour."
                      }]
                    }
    :counting_characters: Counting Characters:
                    Stocktwits limits message length to 140 characters. URLs are one thing that effects character
                    counting. Any message over 140 characters will return and error response.
                    Character Encoding:
                    The Stocktwits API supports UTF-8 encoding and any UTF-8 character counts as a single character.
                    Please note that angle brackets ("<" and ">") are entity-encoded to prevent Cross-Site Scripting
                    attacks for web-embedded consumers of JSON API output. The resulting encoded entities do count
                    towards the 140 character limit. Symbols and characters outside of the standard ASCII range may be
                    translated to HTML entities.
                    URL/Links such as "http://stocktwits.com" will be automatically converted to stks.co or stlk.it
                    links and will represent "20" characters in a message count. You will not need to worry about
                    shortening a link before you create a message. Links are defined as having a protocol such as
                    "http://" or "https://".
    """

    def __init__(self, auth_handler=None,
                 host='api.stocktwits.com', api_root='/api/2',
                 login_host='stocktwits.com', login_root='/api/login',
                 rooms_host='roomapi.stocktwits.com', rooms_root='',
                 avatars_host='avatars.stocktwits.com', avatars_root='/production',
                 charts_host='charts.stocktwits.com', charts_root='/production',
                 ql_host='ql.stocktwits.com', ql_root='',
                 assets_host='assets.stocktwits.com', assets_root='',
                 cache=None, retry_count=0,
                 retry_delay=0, retry_errors=None, timeout=60, parser=None,
                 compression=False, wait_on_rate_limit=False,
                 wait_on_rate_limit_notify=False, proxy=''):
        """
        API instance constructor

        :param auth_handler:
        :param host: url of the server of the base api,
                     default: 'api.stocktwits.com'
        :param login_host: url of the server of the login api,
                     default: 'stocktwits.com'
        :param rooms_host: url of the server of the rooms api,
                     default: 'roomapi.stocktwits.com'
        :param avatars_host: url of the server of the avatars api,
                     default: 'avatars.stocktwits.com'
        :param charts_host: url of the server of the charts api,
                     default: 'charts.stocktwits.com'
        :param ql_host: url of the server of the ql api,
                     default: 'ql.stocktwits.com'
        :param assets_host: url of the server of the assets api,
                     default: 'assets.stocktwits.com'
        :param api_root: suffix of the api version, default: '/api/2'
        :param login_root: suffix of the login version, default: '/api/login'
        :param rooms_root: suffix of the rooms version, default: '/rooms'
        :param avatars_root: suffix of the api version, default: '/production'
        :param charts_root: suffix of the api version, default: '/production'
        :param ql_root: suffix of the api version, default: ''
        :param assets_root: suffix of the api version, default: ''
        :param cache: Cache to query if a GET method is used, default: None
        :param retry_count: number of allowed retries, default: 0
        :param retry_delay: delay in second between retries, default: 0
        :param retry_errors: default: None
        :param timeout: delay before to consider the request as timed out in
                        seconds, default: 60
        :param parser: ModelParser instance to parse the responses,
                       default: None
        :param compression: If the response is compressed, default: False
        :param wait_on_rate_limit: If the api wait when it hits the rate limit,
                                   default: False
        :param wait_on_rate_limit_notify: If the api print a notification when
                                          the rate limit is hit, default: False
        :param proxy: Url to use as proxy during the HTTP request, default: ''

        :raise TypeError: If the given parser is not a ModelParser instance.
        """
        self.auth = auth_handler
        self.host = host
        self.login_host = login_host
        self.rooms_host = rooms_host
        self.avatars_host = avatars_host
        self.charts_host = charts_host
        self.ql_host = ql_host
        self.assets_host = assets_host
        self.api_root = api_root
        self.login_root = login_root
        self.rooms_root = rooms_root
        self.avatars_root = avatars_root
        self.charts_root = charts_root
        self.ql_root = ql_root
        self.assets_root = assets_root
        self.cache = cache
        self.compression = compression
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.timeout = timeout
        self.wait_on_rate_limit = wait_on_rate_limit
        self.wait_on_rate_limit_notify = wait_on_rate_limit_notify
        self.parser = parser or ModelParser()
        self.proxy = {}
        if proxy:
            self.proxy['https'] = proxy
        parser_type = Parser
        if not isinstance(self.parser, parser_type):
            raise TypeError(
                '"parser" argument has to be an instance of "{required}".'
                ' It is currently a {actual}.'.format(
                    required=parser_type.__name__,
                    actual=type(self.parser)
                )
            )

    def stream_user(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-user-docs
            :allowed_param: 'id', 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/user/{id}.json'.format(id=id),
            payload_type='json', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=False
        )

    def stream_symbol(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-symbol-docs
            :allowed_param: 'id', 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/symbol/{id}.json'.format(id=id),
            payload_type='json', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=False
        )

    def stream_friends(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-friends-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/friends.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True
        )

    def stream_mentions(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-mentions-docs
            :allowed_param: 'since', 'max', 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/streams/mentions.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback'],
            require_auth=True
        )

    def stream_direct(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-direct-docs
            :allowed_param: 'since', 'max', 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/streams/direct.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback'],
            require_auth=True
        )

    def stream_direct_sent(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-direct_sent-docs
            :allowed_param: 'since', 'max', 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/streams/direct_sent.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback'],
            require_auth=True
        )

    def direct_received(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-direct_received-docs
            :allowed_param: 'since', 'max', 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/streams/direct_received.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback'],
            require_auth=True
        )

    def stream_watchlist(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-watchlist-docs
            :allowed_param: 'id', 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/watchlist/{id}.json'.format(id=id),
            payload_type='json', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True
        )

    def stream_static_watchlist(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-watchlist-docs
            :allowed_param: 'id', 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/watchlist/static.json',
            payload_type='watchlist', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True
        )

    def stream_all(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-all-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/all.json',
            payload_type='json', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_charts(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-charts-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/charts.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=False
        )

    def stream_equities(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-equities-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/equities.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_forex(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-forex-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/forex.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_futures(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-futures-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/futures.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_private_companies(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-private_companies-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/private_companies.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_suggested(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-suggested-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/suggested.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=False
        )

    def stream_symbols(self, symbols):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-symbols-docs
            :allowed_param: 'symbols', 'since', 'max', 'limit', 'callback', 'filter'
        """
        if isinstance(symbols, list):
            if len(symbols) > 10:
                raise StocktwitError('Symbols list is too big, must be 10 or less.')
            else:
                symbols = ','.join(symbols)
        elif isinstance(symbols, str):
            symbols = symbols.split(',')
            if len(symbols) > 10:
                raise StocktwitError('Symbols list is too big, must be 10 or less.')
            else:
                symbols = ','.join(symbols)
        else:
            raise StocktwitError('Symbols data must be a list or a string (comma delimited) of 1 or more symbols')
        return bind_api(
            api=self,
            path='/streams/symbols.json',
            payload_type='json', payload_list=True,
            allowed_param=['symbols', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )(symbols=symbols)

    def stream_trending(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-trending-docs
            :allowed_param: 'since', 'max', 'limit', 'callback', 'filter'
        """
        return bind_api(
            api=self,
            path='/streams/trending.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'limit', 'callback', 'filter'],
            require_auth=False
        )

    def stream_sectors(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-sectors-docs
            :allowed_param: 'sector_path', 'since', 'max', 'limit', 'callback', 'filter'
            :sector_csv: https://api.stocktwits.com/sectors/Stocktwits-sectors-industries.csv
        """
        return bind_api(
            api=self,
            path='/streams/{sector_path}.json',
            payload_type='json', payload_list=True,
            allowed_param=['sector_path', 'since', 'max', 'limit', 'callback', 'filter'],
            require_auth=True,
            partner_level=True
        )

    def stream_conversation(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#streams-conversation-docs
            :allowed_param: 'id', 'since', 'max', 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/streams/conversation/{id}.json'.format(id=id),
            payload_type='json', payload_list=True,
            allowed_param=['id', 'since', 'max', 'limit', 'callback'],
            require_auth=False
        )

    def me(self):
        """ Get the authenticated user """
        return self.verify_account()['user']['username']

    def search(self, q):
        """ :reference: https://api.stocktwits.com/developers/docs/api#search-index-docs
            :allowed_param: 'q', 'callback'
        """
        return bind_api(
            api=self,
            path='/search.json',
            payload_type='json', payload_list=True,
            allowed_param=['q', 'callback'],
            require_auth=False
        )(q=q)

    def search_symbols(self, q):
        """ :reference: https://api.stocktwits.com/developers/docs/api#search-symbols-docs
            :allowed_param: 'q', 'callback'
        """
        return bind_api(
            api=self,
            path='/search/symbols.json',
            payload_type='json', payload_list=True,
            allowed_param=['q', 'callback'],
            require_auth=False
        )(q=q)

    def search_users(self, q):
        """ :reference: https://api.stocktwits.com/developers/docs/api#search-users-docs
            :allowed_param: 'q', 'callback'
        """
        return bind_api(
            api=self,
            path='/search/users.json',
            payload_type='json', payload_list=True,
            allowed_param=['q', 'callback'],
            require_auth=False
        )(q=q)

    def create_message(self, chart_name=None, chart=None):
        """
        Create a Stocktwits message. To upload a chart to accompany the message, pass a file using the chart parameter.
        The API will check that the character count is under 140, will shorten all links, and prevent duplicate message
        postings.
        The response returned on creating a message is a great way to use Stocktwits context with content sent to
        another non-financially focused social network such as Facebook, LinkedIn or Twitter. By using the body content
        that is returned you will receive the complete message compiled with any shortened links. Because these other
        platforms aren't as investor-focused as Stocktwits they may lack the context like price, chart or video. Sending
        the response's body will allow the user of those other networks access to the financial context of the message
        with a link back to the appropriate page.
        The Message ID can be used to create your own link to the message as a landing page. This comes in handy in the
        case of a Chart or Video where you might not want to create your own webpage or integrate the chart or video
        into your application.
        :reference: https://api.stocktwits.com/developers/docs/api#messages-create-docs
        :allowed_param: 'body', 'in_reply_to_message_id', 'chart', 'sentiment'
        """
        if chart:
            API._pack_image(chart_name, 2097152, c=chart)
        bind_api(
            api=self,
            path='/messages/create.json',
            method='POST',
            payload_type='json', payload_list=False,
            allowed_param=['body', 'in_reply_to_message_id', 'chart', 'sentiment'],
            require_auth=True
        )

    def show_message(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#messages-show-docs
            :allowed_param: 'id', 'conversation', 'callback'
        """
        return bind_api(
            api=self,
            path='/messages/show/{id}.json'.format(id=id),
            payload_type='json', payload_list=False,
            allowed_param=['id', 'conversation', 'callback'],
            require_auth=False
        )

    def like_message(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#messages-like-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/messages/like.json',
            method='POST',
            payload_type='json', payload_list=False,
            allowed_param=['id'],
            require_auth=True
        )(id=id)

    def unlike_message(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#messages-unlike-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/messages/unlike.json',
            method='POST',
            payload_type='json', payload_list=False,
            allowed_param=['id'],
            require_auth=True
        )(id=id)

    @property
    def list_blocks(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#graph-blocking-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/graph/blocking.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'callback'],
            require_auth=True
        )

    @property
    def list_mutes(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#graph-muting-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/graph/muting.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'callback'],
            require_auth=True
        )

    @property
    def list_following(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#graph-following-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/graph/following.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'callback'],
            require_auth=True
        )

    @property
    def list_followers(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#graph-followers-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/graph/followers.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'callback'],
            require_auth=True
        )

    @property
    def list_symbols(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#graph-symbols-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/graph/symbols.json',
            payload_type='json', payload_list=True,
            allowed_param=['since', 'max', 'callback'],
            require_auth=True
        )

    @property
    def recently_viewed_symbols(self):
        """ :reference: https://api.stocktwits.com/api/2/graph/recently_viewed.json
            :allowed_param: ''
        """
        return bind_api(
            api=self,
            path='/graph/recently_viewed.json',
            payload_type='recently_viewed', payload_list=True,
            allowed_param=[],
            require_auth=True
        )

    def create_friendship(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#friendships-create-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/friendships/create/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    def destroy_friendship(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#friendships-destroy-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/friendships/destroy/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def list_watchlists(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-index-docs
            :allowed_param: 'callback'
        """
        return bind_api(
            api=self,
            path='/watchlists.json',
            payload_type='json', payload_list=True,
            allowed_param=['callback'],
            require_auth=True
        )

    def create_watchlist(self, name):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-create-docs
            :allowed_param: 'name'
        """
        return bind_api(
            api=self,
            path='/watchlists/create.json',
            method='POST', payload_list=False,
            payload_type='watchlist',
            allowed_param=['name'],
            require_auth=True
        )(name=name)

    def update_watchlist(self, id, name):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-update-docs
            :allowed_param: 'id', 'name'
        """
        return bind_api(
            api=self,
            path='/watchlists/update/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='watchlist',
            allowed_param=['id', 'name'],
            require_auth=True
        )(name=name)

    def destroy_watchlist(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-destroy-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/watchlists/destroy/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='watchlist',
            allowed_param=['id', 'name'],
            require_auth=True
        )

    def show_watchlist(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-show-docs
            :allowed_param: 'id', 'callback'
        """
        return bind_api(
            api=self,
            path='/watchlists/show/{id}.json'.format(id=id),
            payload_type='watchlist', payload_list=True,
            allowed_param=['id', 'callback'],
            require_auth=True
        )

    def static_watchlist(self):
        """ :reference: https://api.stocktwits.com/api/2/watchlists/static_watchlist.json
            :allowed_param: 'id', 'callback'
        """
        return bind_api(
            api=self,
            path='/watchlists/static_watchlist.json',
            payload_type='watchlist',
            allowed_param=[],
            require_auth=True
        )

    def add_to_watchlist(self, id, symbols):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-symbols-create-docs
            :allowed_param: 'id', 'symbols'
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        return bind_api(
            api=self,
            path='/watchlists/{id}/symbols/create.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='watchlist',
            allowed_param=['id', 'symbols'],
            require_auth=True
        )(symbols=symbols)

    def remove_from_watchlist(self, id, symbols):
        """ :reference: https://api.stocktwits.com/developers/docs/api#watchlists-symbols-destroy-docs
            :allowed_param: 'id', 'symbols'
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        return bind_api(
            api=self,
            path='/watchlists/{id}/symbols/destroy.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='watchlist',
            allowed_param=['id', 'symbols'],
            require_auth=True
        )(symbols=symbols)

    def create_block(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#blocks-create-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/blocks/create/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    def destroy_block(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#blocks-destroy-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/blocks/destroy/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    def create_mute(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#mutes-create-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/mutes/create/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    def destroy_mute(self, id):
        """ :reference: https://api.stocktwits.com/developers/docs/api#mutes-destroy-docs
            :allowed_param: 'id'
        """
        return bind_api(
            api=self,
            path='/mutes/destroy/{id}.json'.format(id=id),
            method='POST', payload_list=False,
            payload_type='user',
            allowed_param=['id'],
            require_auth=True
        )

    def verify_account(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#account-verify-docs
            :allowed_param: 'callback'
        """
        try:
            return bind_api(
                api=self,
                path='/account/verify.json',
                payload_type='user',
                require_auth=True,
                allowed_param=['callback']
            )
        except StocktwitError as e:
            if e.response is not None and e.response.status_code == 401:
                return False
            raise

    @property
    def update_account(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#account-update-docs
            :allowed_param: 'name', 'email', 'username'
        """
        return bind_api(
            api=self,
            path='/account/update.json',
            method='POST',
            payload_type='user',
            allowed_param=['name', 'email', 'username'],
            require_auth=False,
            partner_level=True
        )

    def get_all_social_connections(self):
        """ :reference: https://api.stocktwits.com/api/2/account/get_all_social_connections.json
            :allowed_param:
        """
        return bind_api(
            api=self,
            path='/account/get_all_social_connections.json',
            payload_type='connections',
            allowed_param=[],
            require_auth=True
        )

    def trending_symbols(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#trending-symbols-docs
            :allowed_param: 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/trending/symbols.json',
            payload_type='symbol', payload_list=True,
            allowed_param=['limit', 'callback'],
            require_auth=False
        )

    def trending_equities(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#trending-symbols-equities-docs
            :allowed_param: 'limit', 'callback'
        """
        return bind_api(
            api=self,
            path='/trending/symbols/equities.json',
            payload_type='symbol', payload_list=True,
            allowed_param=['limit', 'callback'],
            require_auth=False
        )

    @property
    def deleted_messages(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#deletions-messages-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/deletions/messages.json',
            payload_type='message',
            allowed_param=['since', 'max', 'callback'],
            require_auth=True,
            partner_level=True
        )

    @property
    def deleted_users(self):
        """ :reference: https://api.stocktwits.com/developers/docs/api#deletions-users-docs
            :allowed_param: 'since', 'max', 'callback'
        """
        return bind_api(
            api=self,
            path='/deletions/users.json',
            payload_type='user',
            allowed_param=['since', 'max', 'callback'],
            require_auth=True,
            partner_level=True
        )

    def heatmap(self, range=None):
        """ :reference: https://api.stocktwits.com/api/2/heatmap/sectors.json
            :allowed_param: 'range'
        """
        if range and range not in ['one', 'six', 'twelve', 'twentyfour']:
            raise StocktwitError('Range must be one of these strings: "one", "six", "twelve", "twentyfour".')
        else:
            range='twentyfour'
        return bind_api(
            api=self,
            path='/heatmap/sectors.json?range={range}'.format(range=range),
            payload_type='sectors',
            allowed_param=['range'], payload_list=True,
            require_auth=False
        )

    def articles(self, stock_tickers=None):
        """ :reference: https://api.stocktwits.com/api/2/articles/stock_articles.json?stock_tickers=ARKQ&stock_tickers=
                        BOTZ
            :allowed_param: 'stock_tickers'
        """
        if stock_tickers and isinstance(stock_tickers, list):
            for ticker in stock_tickers:
                stock_tickers+='stock_tickers={ticker}&'.format(ticker=ticker)
        elif stock_tickers and re.match(r"[A-Z]+(,)*", stock_tickers):
            stock_tickers=stock_tickers.split(',')
            for ticker in stock_tickers:
                stock_tickers+='stock_tickers={ticker}&'.format(ticker=ticker)
        elif stock_tickers and re.match(r"stock_tickers=[A-Z]+&*", stock_tickers):
            pass
        else:
            raise StocktwitError('One or more stock tickers must be passed in order to get a valid response. The stock'
                                  ' ticker(s) should be in the form of a list, a string of comma separated tickers, or '
                                  'a string in the format of "stock_tickers=ARKQ&stock_tickers=BOTZ&stock_tickers=TTD",'
                                  ' for example.')
        return bind_api(
            api=self,
            path='/articles/stock_articles.json?{stock_tickers}',
            payload_type='articles',
            allowed_param=['stock_tickers'], payload_list=True,
            require_auth=True
        )

    def notifications(self):
        """ :reference: https://stocktwits.com/notifications
            :allowed_param: 'type', 'ignore_mark_read', 'since', 'max', 'filter'
            Parameter 'type' can be equal to 'standard' or 'direct_messages'.
            Parameter 'ignore_mark_read' can be equal to 'true' or 'false'.
            Parameter 'since' should be equal to an id, i.e. '32106071'.
            Parameter 'max' should be equal to an id, i.e. '182515389'.
            Parameter 'filter' can be equal to 'all'.
        """
        return bind_api(
            api=self,
            path='/notifications.json',
            payload_type='cursor',
            allowed_param=['type', 'ignore_mark_read', 'since', 'max', 'filter'], payload_list=True,
            require_auth=True
        )

    def unread_notifications(self):
        """ :reference: https://stocktwits.com/notifications
            :allowed_param: 'type', 'ignore_mark_read', 'since', 'max', 'filter'
            Parameter 'type' can be equal to 'standard' or 'direct_messages'.
            Parameter 'ignore_mark_read' can be equal to 'true' or 'false'.
            Parameter 'since' should be equal to an id, i.e. '32106071'.
            Parameter 'max' should be equal to an id, i.e. '182515389'.
            Parameter 'filter' can be equal to 'all'.
        """
        return bind_api(
            api=self,
            path='/notifications/unread.json',
            payload_type='cursor',
            allowed_param=['type', 'ignore_mark_read', 'since', 'max', 'filter'], payload_list=True,
            require_auth=True
        )

    def symbols_full(self, symbol):
        """ :reference: https://api.stocktwits.com/api/2/symbols/show_full/QCOM.json
            :allowed_param: 'symbol'
        """
        return bind_api(
            api=self,
            path='/symbols/show_full/{symbol}.json'.format(symbol=symbol),
            payload_type='symbol',
            allowed_param=['symbol'],
            require_auth=False
        )

    def symbols_articles(self, symbol):
        """ :reference: https://api.stocktwits.com/api/2/symbols/3290/articles.json
            :allowed_param: 'symbol'
        """
        return bind_api(
            api=self,
            path='/symbols/{symbol}/articles.json'.format(symbol=symbol),
            payload_type='articles',
            allowed_param=['symbol'],
            require_auth=False
        )

    def intraday(self, symbol, zoom):
        """ :reference: https://ql.stocktwits.com/intraday?symbol=QCOM&zoom=1d
            :allowed_param: 'symbol', 'zoom'
        """
        return bind_api(
            api=self,
            path='/intraday?symbol={symbol}&zoom={zoom}'.format(symbol=symbol, zoom=zoom),
            payload_type='intraday',
            allowed_param=['symbol', 'zoom'], payload_list=True,
            require_auth=False, ql_api=True
        )


    def intraday_multi(self, symbols):
        """ :reference: https://ql.stocktwits.com/intraday_multi?symbols=QCOM
            :allowed_param: 'symbols'
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        elif isinstance(symbols, str):
            symbols = symbols.split(',')
            symbols = ','.join(symbols)
        else:
            raise StocktwitError('Symbols data must be a list or a string (comma delimited) of 1 or more symbols')
        return bind_api(
            api=self,
            path='/intraday_multi?symbols={symbols}'.format(symbols=symbols),
            payload_type='intraday_multi',
            allowed_param=['symbols'], payload_list=True,
            require_auth=False, ql_api=True
        )

    def batch(self, symbols):
        """ :reference: https://ql.stocktwits.com/batch?symbols=QCOM
            :allowed_param: 'symbols'
        """
        if isinstance(symbols, list):
            symbols = ','.join(symbols)
        elif isinstance(symbols, str):
            symbols = symbols.split(',')
            symbols = ','.join(symbols)
        else:
            raise StocktwitError('Symbols data must be a list or a string (comma delimited) of 1 or more symbols')
        return bind_api(
            api=self,
            path='/batch?symbols={symbols}'.format(symbols=symbols),
            payload_type='json',
            allowed_param=['symbols'], payload_list=True,
            require_auth=False, ql_api=True
        )

    def price_data(self, symbol, fundamentals=True):
        """ :reference: https://ql.stocktwits.com/pricedata?symbol=QCOM&fundamentals=true
            :allowed_param: 'symbols'
        """
        return bind_api(
            api=self,
            path='/intraday_multi?symbol={symbol}&fundamentals={fundamentals}'.format(symbol=symbol,
                                                                                      fundamentals=fundamentals),
            payload_type='price_data',
            allowed_param=['symbols'], payload_list=True,
            require_auth=False, ql_api=True
        )

    def sentiment(self, symbol):
        """ :reference: https://api.stocktwits.com/api/2/symbols/QCOM/sentiment.json
            :allowed_param: 'symbol'
        """
        return bind_api(
            api=self,
            path='/symbols/{symbol}/sentiment.json'.format(symbol=symbol),
            payload_type='sentiment',
            allowed_param=['symbol'], payload_list=True,
            require_auth=False
        )

    def volume(self, symbol):
        """ :reference: https://api.stocktwits.com/api/2/symbols/SJM/volume.json
            :allowed_param: 'symbol'
        """
        return bind_api(
            api=self,
            path='/symbols/{symbol}/volume.json'.format(symbol=symbol),
            payload_type='data',
            allowed_param=['symbol'], payload_list=True,
            require_auth=False
        )

    def earnings_calendar(self):
        """ :reference: https://api.stocktwits.com/api/2/discover/earnings_calendar?date_from=&date_to=
            :allowed_param: 'date_from', 'date_to'
        """
        return bind_api(
            api=self,
            path='/discover/earnings_calendar?date_from=&date_to=',
            payload_type='earnings',
            allowed_param=['date_from', 'date_to'],
            require_auth=False
        )

    def room(self, slug):
        """ :reference: https://roomapi.stocktwits.com/room/api_test
            :allowed_param: 'slug'
        """
        return bind_api(
            api=self,
            path='/room/{slug}'.format(slug=slug),
            payload_type='room',
            allowed_param=['slug'],
            require_auth=True, rooms_api=True
        )

    def room_role(self, slug):
        """ :reference: https://roomapi.stocktwits.com/room/api_test/role
            :allowed_param: 'slug'
        """
        return bind_api(
            api=self,
            path='/room/{slug}/role'.format(slug=slug),
            payload_type='role',
            allowed_param=['slug'],
            require_auth=True, rooms_api=True
        )

    def room_messages(self, slug):
        """ :reference: https://roomapi.stocktwits.com/room/api_test/messages?flat=1&limit=30&order=newest&until=
            :allowed_param: 'slug', 'flat', 'limit', 'order', 'until'
        """
        return bind_api(
            api=self,
            path='/room/{slug}/messages?'.format(slug=slug),
            payload_type='room_messages',
            allowed_param=['slug', 'flat', 'limit', 'order', 'until'],
            require_auth=True, rooms_api=True
        )

    def rooms(self):
        """ :reference: https://roomapi.stocktwits.com/rooms?role=any&limit=100
            :allowed_param: 'role', 'limit', 'filters'
        """
        return bind_api(
            api=self,
            path='/rooms',
            payload_type='rooms',
            allowed_param=['role', 'limit', 'filters'],
            require_auth=True, rooms_api=True
        )

    def room_topics(self):
        """ :reference: https://roomapi.stocktwits.com/topics
            :allowed_param:
        """
        return bind_api(
            api=self,
            path='/topics',
            payload_type='list',
            allowed_param=[''], payload_list=True,
            require_auth=False, rooms_api=True
        )

    def featured_rooms(self):
        """ :reference: https://roomapi.stocktwits.com/rooms/featured
            :allowed_param:
        """
        return bind_api(
            api=self,
            path='/rooms/featured',
            payload_type='json',
            allowed_param=[],
            require_auth=False, rooms_api=True
        )

    def room_status(self):
        """ :reference: https://roomapi.stocktwits.com/rooms/status
            :allowed_param:
        """
        return bind_api(
            api=self,
            path='/rooms/status',
            payload_type='json',
            allowed_param=[],
            require_auth=False, rooms_api=True
        )

    def conversations(self):
        """ :reference: https://api.stocktwits.com/api/2/direct_messages/conversations.json?filter=all
            :allowed_param: 'filter'
        """
        return bind_api(
            api=self,
            path='/direct_messages/conversations.json',
            payload_type='json',
            allowed_param=['filter'],
            require_auth=True
        )

    def user_extended(self, user):
        """ :reference: https://api.stocktwits.com/api/2/users/Spekoliunas/extended.json
            :allowed_param: 'user'
        """
        return bind_api(
            api=self,
            path='/users/{user}/extended.json'.format(user=user),
            payload_type='user',
            allowed_param=['user'],
            require_auth=False
        )

    def user_tooltip(self, user):
        """ :reference: https://api.stocktwits.com/api/2/users/mikepie/tooltip.json
            :allowed_param: 'user'
        """
        return bind_api(
            api=self,
            path='/users/{user}/tooltip.json'.format(user=user),
            payload_type='user',
            allowed_param=['user'],
            require_auth=False
        )

    def stock_related(self, symbol):
        """ :reference: https://api.stocktwits.com/api/2/relations/AMC/stock_related_combined.json
            :allowed_param: 'symbol'
        """
        return bind_api(
            api=self,
            path='/relations/{symbol}/stock_related_combined.json'.format(symbol=symbol),
            payload_type='symbol',
            allowed_param=['symbol'],
            require_auth=False
        )

    def global_announcement(self):
        """ :reference: https://api.stocktwits.com/api/2/global_announcement?platform=web
            :allowed_param: 'platform'
        """
        return bind_api(
            api=self,
            path='/global_announcement',
            payload_type='announcements',
            allowed_param=['platform'],
            require_auth=False
        )

    def account_preferences(self):
        """ :reference: https://api.stocktwits.com/api/2/account/preferences.json
            :allowed_param:
        """
        return bind_api(
            api=self,
            path='/account/preferences.json',
            payload_type='user',
            allowed_param=[],
            require_auth=False
        )


    """ Internal use only """

    @staticmethod
    def _pack_image(chart_name, max_size, form_field='chart', c=None):
        """Pack image from file into multipart-formdata post body"""
        # image must be less than 2MB in size
        if c is None:
            try:
                if os.path.getsize(chart_name) > max_size:
                    raise StocktwitError('File is too big, must be less than %skb.'
                                          % max_size)
            except os.error as e:
                raise StocktwitError('Unable to access file: %s' % e.strerror)

            # build the multipart-formdata body
            fp = open(chart_name, 'rb')
        else:
            c.seek(0, 2)  # Seek to end of file
            if c.tell() > max_size:
                raise StocktwitError('File is too big, must be less than %skb.'
                                      % max_size)
            c.seek(0)  # Reset to beginning of file
            fp = c

        # image must be gif, jpeg, or png
        file_type = mimetypes.guess_type(chart_name)
        if file_type is None:
            raise StocktwitError('Could not determine file type')
        file_type = file_type[0]
        if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
            raise StocktwitError('Invalid file type for image: %s' % file_type)

        if isinstance(chart_name, six.text_type):
            chart_name = chart_name.encode('utf-8')

        boundary = b'Tw3ePy'
        body = [b'--' + boundary, 'Content-Disposition: form-data; name="{0}";'
                                  ' filename="{1}"'.format(form_field, chart_name)
            .encode('utf-8'), 'Content-Type: {0}'.format(file_type).encode('utf-8'), b'', fp.read(),
                b'--' + boundary + b'--', b'']
        fp.close()
        body = b'\r\n'.join(body)

        # build headers
        headers = {
            'Content-Type': 'multipart/form-data; boundary=Tw3ePy',
            'Content-Length': str(len(body))
        }

        return headers, body
