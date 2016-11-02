import base64
import datetime
import inspect
from abc import ABCMeta

from framework.utils.date_utils import DateUtils
from framework.utils.id import Id
import copy


class Serializeable(metaclass=ABCMeta):
    _context=None
    
    @classmethod
    def get_definition(cls):
        # abstract, returns definition config
        return None

    @classmethod
    def get_definition_for_keys(cls, optional_keys=None,for_api=False):
        # returns the required definition plus
        # any optional keys in the "optional_keys" array/dict

        defn = cls.get_definition()
        if defn is None:
            return None

        key_list = cls._get_optional_keys_for_class(optional_keys)
        key_dict = {key: True for key in key_list}

        ret = {}
        for key, attr in defn.items():
            if attr.is_required() or (for_api and attr.is_required_for_api()) or key in key_dict:
                ret[key] = attr

        return ret

    @classmethod
    def get_key_to_type(cls, optional_keys):

        return cls._recursive_key_to_type([], optional_keys)

    @classmethod
    def _get_optional_keys_for_class(cls, optional_keys=None):
        try:
            if isinstance(optional_keys, list):
                return optional_keys
            else:
                all_classes = inspect.getmro(cls)
                for parent_cls in all_classes:
                    if parent_cls.__name__ in optional_keys:
                        return optional_keys[parent_cls.__name__]

        except (TypeError, KeyError):
            pass

        return []

    def to_dict(self, stringify_ids=False, optional_keys=None, for_api=False):
        d = self._recursive_to_dict([], stringify_ids, optional_keys, for_api)

        return d

    def _recursive_to_dict(self, seen_refs, stringify_ids, optional_keys=None, for_api=False):
        # if we have a circular reference, then simply exit
        if self in seen_refs:
            raise CircularRefException()

        seen_refs.append(self)

        state = {
            "object": self.__class__.__name__
        }

        defn = self.get_definition_for_keys(optional_keys,for_api)

        for key in self._get_keys(optional_keys,for_api):
            if not self._include_key(key, defn):
                continue

            try:
                value = getattr(self, key)
                if hasattr(value, '__call__'):
                    # whoops it looks like a function
                    raise AttributeError()
            except AttributeError:
                value = self._get_attr(key)

            try:
                dict = value._recursive_to_dict(copy.copy(seen_refs), stringify_ids, optional_keys, for_api)
                state[key] = dict
            except AttributeError:
                new_value = value
                if stringify_ids:
                    new_value = self._stringify_id(value)

                state[key] = new_value
            except CircularRefException:
                pass  # skip circular references

        return state

    def _include_key(self, key, defn):
        if defn is None:
            return True
        return key in defn

    def _stringify_id(self, value):
        # try int
        try:
            if value > Id.MAX_32_BIT_INT:
                return str(value)
        except (TypeError, AttributeError) as e:
            pass

        if isinstance(value, datetime.datetime):
            return DateUtils.datetime_to_unix(value)

        # try bytes
        try:
            return base64.standard_b64encode(value).decode("utf-8")
        except (TypeError, AttributeError) as e:
            pass

        return value

    def _get_keys(self, opitional_keys = None,for_api=False):
        if self._() is not None:
            return self.get_definition_for_keys(opitional_keys,for_api)
        return []

    def _get_attr(self, key):
        defn = self.get_definition()
        required = False
        if defn is not None and key in defn:
            if defn[key].is_lazy():
                return defn[key].get_lazy_value(self)
            required = defn[key].is_required()

        if required:
            raise AttributeError(key)

        return None
    
    
    def _get_context(self):
        if self._context:
            return self._context
        else:
            return {}
    
    def set_context(self, context):
        """
            Used for serializing things that require the logged-in user as a context
        """
        self._context = context


class CircularRefException(Exception):
    def __init__(self):
        super().__init__("Circular reference while serializing object")
