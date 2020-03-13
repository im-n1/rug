# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

import logging

from requests_oauthlib import OAuth2Session, OAuth2

from stocktwits.api import API
from stocktwits.error import StocktwitError

log = logging.getLogger(__name__)


class AuthHandler(object):
    def apply_auth(self, url, method, headers, parameters):
        """Apply authentication headers to request"""
        raise NotImplementedError
    def get_username(self):
        """Return the username of the authenticated user"""
        raise NotImplementedError

class WebAppAuthHandler(AuthHandler):
    """ Web-Application-only authentication handler
        :reference: https://api.stocktwits.com/developers/docs/authentication
    """
    OAUTH_HOST = 'api.stocktwits.com/api/2/'
    OAUTH_ROOT = 'oauth/'
    def __init__(self, consumer_key, consumer_secret, redirect_uri):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.redirect_uri = redirect_uri
        self.scope = 'read,watch_lists,direct_messages,publish_messages,publish_watch_lists,follow_users,follow_stocks'
        self.authorization_url = None
        self.state = None
        self.authorization_response = None
        self.user = None
        self.username = None
        self.oauth = OAuth2Session(consumer_key, redirect_uri=redirect_uri, scope=self.scope)
        self.authorization_url, self.state = self.oauth.authorization_url(self._get_oauth_url('authorize'))
        print('Please go here and authorize: ', self.authorization_url)
        self.authorization_response = str(input('Enter the full callback URL: '))
        self.user = self.oauth.fetch_token(self._get_oauth_url('token'),
                                           authorization_response=self.authorization_response,
                                           include_client_id = True, client_secret=self.consumer_secret)
        self.access_token = self.user['access_token']
    def _get_oauth_url(self, endpoint):
        return 'https://' + self.OAUTH_HOST + self.OAUTH_ROOT + endpoint
    def apply_auth(self, url, method, headers, parameters):
        return OAuth2(self.consumer_key, token=self.user['access_token'])
    def get_username(self):
        if self.username is None:
            api = API(self)
            user = api.verify_account()
            if user:
                self.username = user.screen_name
            else:
                raise StocktwitError('Unable to get username,'
                                      ' invalid oauth token!')
        return self.username

class SignInAuthHandler(AuthHandler):
    # TODO: add this functionality
    """ Mimic the registration and sign-in process the uses a "Connect with Stocktwits" button.
        :reference: https://api.stocktwits.com/developers/docs/signin
    """
    OAUTH_HOST = 'api.stocktwits.com/api/2/'
    OAUTH_ROOT = 'oauth/'
    def __init__(self, consumer_key, consumer_secret, redirect_uri):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.redirect_uri = redirect_uri
        self.scope = 'read,watch_lists,direct_messages,publish_messages,publish_watch_lists,follow_users,follow_stocks'
        self.authorization_url = None
        self.state = None
        self.authorization_response = None
        self.user = None
        self.username = None
    def apply_auth(self, url, method, headers, parameters):
        return OAuth2(self.consumer_key, token=self.user['access_token'])
    def get_username(self):
        if self.username is None:
            api = API(self)
            user = api.verify_account()
            if user:
                self.username = user.screen_name
            else:
                raise StocktwitError('Unable to get username,'
                                      ' invalid oauth token!')
        return self.username
