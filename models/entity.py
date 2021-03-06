import copy
import datetime
import pprint

import framework.models.data_access_object
from framework.models.serializeable import Serializeable
from framework.utils.multi_shard_query import MultiShardQuery
from framework.utils.type import Type

###

# Entity shouldn't be an ABC because it can be used stand-alone
class Entity(Serializeable):
    # this is the state when fetched from the DAO
    _stored_state = None

    # this is the state after domain modifications
    _current_state = None

    _deleted = False

    def __init__(self, id):
        # should override with required arguments
        # to satisfy all invariants
        # all domain objects must have an id
        self._stored_state = {}
        self._current_state = {}
        self._set_attr("id", id)

    @property
    def id(self):
        return self._get_attr("id")

    @property
    def is_new(self):
        return not self._stored_state

    @property
    def is_dirty(self):
        dirty_keys = self.get_dirty_keys()

        return not not dirty_keys

    @property
    def deleted(self):
        return self._deleted

    def set_deleted(self):
        self._deleted = True
        if "modified_ts" in self._current_state or "modified_ts" in self._stored_state:
            self._current_state["modified_ts"]=datetime.datetime.now()

    def _recursive_to_dict(self, seen_refs, stringify_ids, optional_keys=None, for_api=False):
        d = super()._recursive_to_dict(seen_refs, stringify_ids, optional_keys=optional_keys,for_api=for_api)
        d["deleted"] = self.deleted

        return d

    def is_key_dirty(self, key):
        dirty_keys = self.get_dirty_keys()

        return key in dirty_keys

    def get_dirty_keys(self):
        dirty_keys = {}
        for key in self._get_keys():
            current_val = self._get_attr(key)
            if not key in self._stored_state or self._stored_state[key] != current_val:
                dirty_keys[key] = current_val
        
        if self.deleted:
            dirty_keys["deleted"]=True

        return dirty_keys

    def _get_keys(self, opitional_keys = None,for_api=False):
        ret = set().union(self._stored_state.keys(), self._current_state.keys())
        defn =  self.get_definition_for_keys(opitional_keys,for_api)
        if defn:
            ret = set().union(defn.keys(), ret)
        return ret

    def revert_to_stored_state(self):
        self._current_state = copy.copy(self._stored_state)

    def update_stored_state(self):
        self._stored_state = copy.copy(self._current_state)

    def _set_attr(self, key, value, default_value=None):
        if value is None:
            value = default_value
        else:
            # make sure inputs match definition
            d = self.get_definition()
            if d and key in d:
                value = Type.coerce_type(value, d[key].get_type())

        self._current_state[key] = value

    def _get_attr(self, key):
        if key in self._current_state:
            return self._current_state[key]
        elif key in self._stored_state:
            return self._stored_state[key]
        else:
            return super()._get_attr(key)


class InvalidParameterError(Exception):
    def __init__(self, parameter_name, value_provided, expecting_description=None):
        super().__init__(self._create_message(parameter_name, value_provided, expecting_description))

    def _create_message(self, param, value, exp=None):
        ret = "Invalid parameter '" + param + "',"
        if exp is not None:
            ret = ret + " expecting " + exp

        ret = ret + " but got '" + pprint.pformat(value) + "'"

        return ret


class EntityDAO(framework.models.data_access_object.DataAccessObject):
    _table = None

    def __init__(self, entity_class, table_name):
        super().__init__(entity_class)
        self._table = table_name

    def get(self, id):
        if self._model_in_cache(id):
            return self._model_cache_get(id)

        rows = self._primary_get(id)

        if not len(rows):
            raise framework.models.data_access_object.RowNotFoundException()

        model = self._row_to_model(rows[0])
        model.update_stored_state()

        self._model_cache_set(model)

        return model

    def _primary_get(self, id):
        return self._get(self._table, ["id"], [id])

    def get_list(self, id_list):
        ret = []
        ids_to_find = []

        for id in id_list:
            if self._model_in_cache(id):
                ret.append(self._model_cache_get(id))
            else:
                ids_to_find.append(id)

        if len(ids_to_find):
            rows = self._primary_get_list(ids_to_find)

            if not self.return_deleted:
                rows = self._filter_deleted(rows)

            for row in rows:
                model = self._row_to_model(row)
                model.update_stored_state()

                self._model_cache_set(model)
                ret.append(model)

        # sort list by original order since it gets messed up with cache and shards
        list_map = {id: index for index, id in enumerate(id_list)}
        ret = sorted(ret, key=lambda row: list_map.get(row.id))

        return ret

    def _primary_get_list(self, id_list):
        return MultiShardQuery(self._pool()).multi_shard_in_list_query(
            id_list, "SELECT * FROM " + self._table + " WHERE id in %l", None)

    def save(self, model):
        return self.save_list([model])

    def save_list(self, models):
        # saves a list of models with the assumption that they all belong on the same shard
        # otherwise, use save() to save one at a time
        models_to_save = []

        for model in models:
            if not model.is_dirty:
                continue

            if model.deleted:
                self.remove_from_cache(model.id)
            else:
                self._model_cache_set(model)

            models_to_save.append(model)
            model.update_stored_state()

        return self._save_list(self._table, models_to_save)

    def _save_list(self, table, models, shard_by_col="id"):
        if not len(models):
            return 0

        dicts = [self._model_to_row(model) for model in models]
        d = dicts[0]

        return MultiShardQuery(self._pool()).multi_shard_insert(
            table,
            shard_by_col,
            dicts,
            self._get_columns_to_update(d.keys()))

    def _primary_save(self, dict):
        cols_to_update = [k for k in self._get_columns_to_update(dict.keys())]

        ret = self._save(self._table, dict, cols_to_update, dict['id'])

        return ret

    def _get_columns_to_update(self, all_columns):
        return [k for k in all_columns if (k != "id" and k != "created_ts")]

    def delete(self, id):
        self.remove_from_cache(id)

        return self._save(self._table, {"id": id, "deleted": 1, "modified_ts": datetime.datetime.now()},
                          ["deleted", "modified_ts"], id)
