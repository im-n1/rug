# stocktwits
# Copyright 2019 John Patrick Roach
# See LICENSE for details.

from __future__ import absolute_import

from rug.stocktwits.official.utils import parse_datetime


class ResultSet(list):
    """A list like object that holds results from a StockTwits API query."""
    def __init__(self, max_id=None, since_id=None):
        super(ResultSet, self).__init__()
        self._max_id = max_id
        self._since_id = since_id

    @property
    def max_id(self):
        if self._max_id:
            return self._max_id
        ids = self.ids()
        # Max_id is always set to the *smallest* id, minus one, in the set
        return (min(ids) - 1) if ids else None

    @property
    def since_id(self):
        if self._since_id:
            return self._since_id
        ids = self.ids()
        # Since_id is always set to the *greatest* id in the set
        return max(ids) if ids else None

    def ids(self):
        return [item.id for item in self if hasattr(item, 'id')]


class Model(object):

    def __init__(self, api=None):
        self._api = api

    def __getstate__(self):
        # pickle
        pickle = dict(self.__dict__)
        try:
            del pickle['_api']  # do not pickle the API reference
        except KeyError:
            pass
        return pickle

    @classmethod
    def parse(cls, api, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError

    @classmethod
    def parse_list(cls, api, json_list):
        """
            Parse a list of JSON objects into
            a result set of model instances.
        """
        results = ResultSet()

        # Handle map parameter for statuses/lookup
        if isinstance(json_list, dict) and 'id' in json_list:
            for _id, obj in json_list['id'].items():
                if obj:
                    results.append(cls.parse(api, obj))
                else:
                    results.append(cls.parse(api, {'id': int(_id)}))
            return results

        for obj in json_list:
            if obj:
                results.append(cls.parse(api, obj))
        return results

    def __repr__(self):
        state = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(state))


class Message(Model):

    @classmethod
    def parse(cls, api, json):
        message = cls(api)
        setattr(message, '_json', json)
        for k, v in json.items():
            if k == 'user':
                user_model = getattr(api.parser.model_factory, 'user') if api else User
                user = user_model.parse(api, v)
                setattr(message, 'user', user)
            elif k == 'created_at':
                setattr(message, k, parse_datetime(v))
            elif k == 'source':
                source_model = getattr(api.parser.model_factory, 'source') if api else Source
                source = source_model.parse(api, v)
                setattr(message, 'source', source)
            elif k == 'symbols':
                symbols_model = getattr(api.parser.model_factory, 'symbol') if api else Symbol
                symbols = symbols_model.parse_list(api, v)
                setattr(message, 'symbols', symbols)
            elif k == 'entities':
                entities_model = getattr(api.parser.model_factory, 'entity') if api else Entity
                entities = entities_model.parse(api, v)
                setattr(message, 'entities', entities)
            elif k == 'conversation':
                conversation_model = getattr(api.parser.model_factory, 'conversation') if api else Conversation
                conversation = conversation_model.parse(api, v)
                setattr(message, 'conversation', conversation)
            elif k == 'recipient':
                recipient_model = getattr(api.parser.model_factory, 'recipient') if api else Recipient
                recipient = recipient_model.parse(api, v)
                setattr(message, 'recipient', recipient)
            elif k == 'parent':
                parent_model = getattr(api.parser.model_factory, 'parent') if api else Parent
                parent = parent_model.parse(api, v)
                setattr(message, 'recipient', parent)
            else:
                setattr(message, k, v)
        return message

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['messages']
        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def create(self):
        return self._api.create_message(self.id)

    def show(self):
        return self._api.show_message(self.id)

    def like(self):
        return self._api.like_message(self.id)

    def unlike(self):
        return self._api.unlike_message(self.id)

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.id == other.id

        return NotImplemented

    def __ne__(self, other):
        result = self == other

        if result is NotImplemented:
            return result

        return not result


class User(Model):

    @classmethod
    def parse(cls, api, json):
        user = cls(api)
        setattr(user, '_json', json)
        for k, v in json.items():
            setattr(user, k, v)
        return user

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['users']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def following(self, **kwargs):
        return self._api.list_following(user_id=self.id, **kwargs)

    def followers(self, **kwargs):
        return self._api.list_followers(user_id=self.id, **kwargs)

    def blocks(self, **kwargs):
        return self._api.list_blocks(user_id=self.id, **kwargs)

    def mutes(self, **kwargs):
        return self._api.list_mutes(user_id=self.id, **kwargs)

    def symbols(self, **kwargs):
        return self._api.list_symbols(user_id=self.id, **kwargs)

    def follow(self):
        self._api.create_friendship(user_id=self.id)

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)

    def block(self):
        self._api.create_block(user_id=self.id)

    def unblock(self):
        self._api.destroy_block(user_id=self.id)

    def mute(self):
        self._api.create_mute(user_id=self.id)

    def unmute(self):
        self._api.destroy_mute(user_id=self.id)

    def watchlists(self, **kwargs):
        return self._api.list_watchlists(user_id=self.id, **kwargs)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id

        return NotImplemented

    def __ne__(self, other):
        result = self == other

        if result is NotImplemented:
            return result

        return not result


class Source(Model):

    @classmethod
    def parse(cls, api, json):
        source = cls(api)
        for k, v in json.items():
            setattr(source, k, v)
        return source


class Symbol(Model):

    @classmethod
    def parse(cls, api, json):
        symbol = cls(api)
        for k, v in json.items():
            setattr(symbol, k, v)
        return symbol

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['symbols']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results

    def add_to_watchlist(self):
        return self._api.add_to_watchlist(self.id)

    def remove_from_watchlist(self):
        return self._api.remove_from_watchlist(self.id)


class Entity(Model):

    @classmethod
    def parse(cls, api, json):
        entity = cls(api)
        for k, v in json.items():
            setattr(entity, k, v)
        return entity


class Parent(Model):

    @classmethod
    def parse(cls, api, json):
        parent = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(parent, k, parse_datetime(v))
            else:
                setattr(parent, k, v)
        return parent


class Conversation(Model):

    @classmethod
    def parse(cls, api, json):
        conversation = cls(api)
        for k, v in json.items():
            setattr(conversation, k, v)
        return conversation


class Recipient(Model):

    @classmethod
    def parse(cls, api, json):
        recipient = cls(api)
        for k, v in json.items():
            setattr(recipient, k, v)
        return recipient


class Result(Model):

    @classmethod
    def parse(cls, api, json):
        result = cls(api)
        for k, v in json.items():
            setattr(result, k, v)
        return result

class Friendship(Model):

    @classmethod
    def parse(cls, api, json):
        relationship = json['relationship']

        # parse source
        source = cls(api)
        setattr(source, '_json', relationship['source'])
        for k, v in relationship['source'].items():
            setattr(source, k, v)

        # parse target
        target = cls(api)
        setattr(target, '_json', relationship['target'])
        for k, v in relationship['target'].items():
            setattr(target, k, v)

        return source, target


class SearchResults(ResultSet):

    @classmethod
    def parse(cls, api, json):
        results = SearchResults()
        result_model = getattr(api.parser.model_factory, 'result') if api else Result
        for result in json['results']:
            results.append(result_model.parse(api, result))
        return results


class Watchlist(Model):

    @classmethod
    def parse(cls, api, json):
        watchlist = Watchlist(api)
        setattr(watchlist, '_json', json)
        for k, v in json.items():
            if k == 'user':
                setattr(watchlist, k, User.parse(api, v))
            elif k == 'created_at':
                setattr(watchlist, k, parse_datetime(v))
            elif k == 'updated_at':
                setattr(watchlist, k, parse_datetime(v))
            else:
                setattr(watchlist, k, v)
        return watchlist

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        if isinstance(json_list, dict):
            json_list = json_list['watchlists']
        for obj in json_list:
            results.append(cls.parse(api, obj))
        return results

    def create(self, **kwargs):
        return self._api.create_watchlist(**kwargs)

    def update(self, **kwargs):
        return self._api.update_watchlist(self.id, **kwargs)

    def destroy(self):
        return self._api.destroy_watchlist(self.id)

    def show(self):
        return self._api.show_watchlist(self.id)

    def static(self):
        return self._api.static_watchlist(self.id)

    def add_symbols(self, ids):
        return self._api.add_to_watchlist(self.id, ids)

    def remove_symbols(self, ids):
        return self._api.remove_from_watchlist(self.id, ids)


class JSONModel(Model):

    @classmethod
    def parse(cls, api, json):
        return json


class IDModel(Model):

    @classmethod
    def parse(cls, api, json):
        if isinstance(json, list):
            return json
        else:
            return json['ids']


class Media(Model):

    @classmethod
    def parse(cls, api, json):
        media = cls(api)
        for k, v in json.items():
            setattr(media, k, v)
        return media


class Cursor(Model):

    @classmethod
    def parse(cls, api, json):
        cursor = cls(api)
        for k, v in json.items():
            setattr(cursor, k, v)
        return cursor

class ModelFactory(object):
    """
    Used by parsers for creating instances
    of models. You may subclass this factory
    to add your own extended models.
    """

    user = User
    message = Message
    source = Source
    symbol = Symbol
    entity = Entity
    conversation = Conversation
    recipient = Recipient
    result = Result
    friendship = Friendship
    search_results = SearchResults
    watchlist = Watchlist
    media = Media
    json = JSONModel
    ids = IDModel
