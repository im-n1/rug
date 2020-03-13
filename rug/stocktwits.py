import httpx


class BaseAPI:
    def _get(self, *args):
        """
        TBD
        """

        return httpx.get(*args)


class UnofficialAPI(BaseAPI):
    """
    Unofficial API wrapper class.
    Unofficial means this class calls some hidden endpoints
    and provides data that official API doesn't. Also doesn't
    need an authorization.
    """

    def __init__(self, symbol):
        """
        Constructor.

        :param str symbol: Symbol of te item we wanna get info about.
        """

        self.symbol = str(symbol)

    def get_dividends(self):
        """
        Fetches symbol dividends with following fields:

        * yield
        * sector_average_yield
        * payment_date
        * ex_date
        * receive_date
        * growth_since

        :return: List of dividend objects.
        :rtype: list
        """

        response = self._get(
            f"https://www.tipranks.com/api/stocks/getChartPageData/?ticker={self.symbol}"
        )
        data = response.json()

        dividends = []

        for item in data["dividends"]:
            dividends.append(
                {
                    "yield": item["yield"],
                    "sector_average_yield": item["sectorYield"],
                    "payment_date": item["payDate"],
                    "ex_date": item["exDate"],
                    "receive_date": item["recDate"],
                    "growth_since": item["growthSinceDate"],
                }
            )

        return dividends

    def get_year_highs_and_lows(self):
        """
        Fetches highs and lows for each year - maximum 7 years back.

        Each year has following fields:

        * year
        * high
        * low

        :return: List of years with the data.
        :rtype: list
        """

        response = self._get(
            f"https://www.tipranks.com/api/stocks/getChartPageData/?ticker={self.symbol}"
        )
        data = response.json()

        return data["historicalHighLow"]


class OfficialAPI(BaseAPI):
    """
    Official API wrapper class.
    Official means this class calls only non-hidden endpoints,
    including some that require authentication.

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


