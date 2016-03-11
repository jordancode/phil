import app.models.user
import framework.models.data_access_object
from framework.models.authentication import Authentication, AuthException
import framework.models.session
from framework.storage.mysql import MySQL
from framework.utils.class_loader import ClassLoader


class AuthDAO(framework.models.data_access_object.DataAccessObject):
    def __init__(self):
        super().__init__(Authentication)

    def new_auth(self, auth_class, provider_id, secret, user, expires_ts=None):
        pid = self._generate_id_from_provider_id(provider_id)

        return auth_class(pid, provider_id, secret, user.id, secret_hashed=False, expires_ts=expires_ts)

    def get_auth_by_id(self, auth_id, user=None):
        rows = MySQL.get(auth_id).query("SELECT * FROM auth WHERE id=%s", (auth_id,))

        if not len(rows):
            raise NoAuthFoundException("_id" + str(auth_id))

        row = rows[0]

        if user is None:
            user_dao = app.models.user.UserDAO()
            user = user_dao.get(row['user_id'])
        elif user.id != row['user_id']:
            raise UserAuthMismatchError()

        auth = self._row_to_model(row)
        auth.update_stored_state()

        return auth

    def get_auth_by_provider_id(self, auth_class, provider_id):
        type_id = self._class_to_type_id(auth_class)
        shard_id = MySQL.get_shard_id_for_string(provider_id)

        rows = MySQL.get_by_shard_id(shard_id).query("SELECT * FROM auth WHERE provider_id=%s AND provider_type=%s",
                                                     (provider_id, type_id))

        if not len(rows):
            raise NoAuthFoundException(provider_id)

        row = rows[0]

        auth = self._row_to_model(row)
        auth.update_stored_state()

        return auth

    def get_auth_for_user(self, user_id, auth_class=None):

        cols = ["user_id"]
        vals = [user_id]
        if auth_class is not None:
            auth_type = self._class_to_type_id(auth_class)
            cols.append("provider_type")
            vals.append(auth_type)

        rows = self._get("auth_lookup", cols, vals, user_id)
        rows = self._filter_deleted(rows)

        return [self._row_to_model(row) for row in rows]

    def save(self, auth):
        if not auth.is_dirty:
            return False

        params = self._model_to_row(auth)
        params["deleted"] = 0

        result = self._save("auth", params, ["id", "user_id", "secret", "created_ts", "expires_ts", "deleted"], auth.id)
        self._save("auth_lookup", params, ["id", "user_id", "secret", "created_ts", "expires_ts", "deleted"],
                   auth.user_id)

        auth.update_stored_state()

        return result

    def _model_to_row(self, model):
        dict = super()._model_to_row(model)
        dict["provider_type"] = self._class_to_type_id(model.__class__)
        return dict

    def _row_to_model(self, row):
        if row['deleted']:
            raise framework.models.data_access_object.RowDeletedException()

        auth_class = self._type_id_to_class(row['provider_type'])
        auth = auth_class(row['id'], row['provider_id'].decode("utf-8"), row['secret'].decode("utf-8"), row["user_id"],
                          secret_hashed=True, expires_ts=row["expires_ts"])

        return auth

    def _generate_id_from_provider_id(self, provider_id):
        shard_id = MySQL.get_shard_id_for_string(provider_id)
        return MySQL.next_id(shard_id)

    def _type_id_to_class(self, type_id):
        return ClassLoader("auth").get_class(type_id)

    def _class_to_type_id(self, auth_class):
        return ClassLoader("auth").get_type_id(auth_class)


class UserAuthMismatchError(AuthException):
    def __str__(self):
        return "auth id does not belong to provided user object"


class NoAuthFoundException(AuthException):
    _provider_id = None

    def __init__(self, provider_id):
        self._provider_id = provider_id

    def __str__(self):
        return "auth row for " + str(self._provider_id) + " does not exist"


class AuthService:
    def log_in(self, auth_class, provider_id, secret, user_agent, time = None):
        """
           returns a user_id
           else throws an authentication exception
        """

        dao = AuthDAO()

        # throws NoAuthFoundException
        auth = dao.get_auth_by_provider_id(auth_class, provider_id)

        if not auth.verify_secret(secret):
            raise InvalidCredentialsException()

        session_dao = framework.models.session.SessionDAO()

        session = session_dao.new_session(auth, user_agent)
        session_dao.save(session)

        # update access token
        dao.save(auth)

        return session

    def add_auth_to_user(self, user, auth_class, provider_id, secret, user_agent, expires_ts=None):
        """
           returns a session
           else throws an authentication exception
        """

        dao = AuthDAO()

        try:
            auth = dao.get_auth_by_provider_id(auth_class, provider_id)

            raise ProviderIdTakenException(auth)

        except (NoAuthFoundException, framework.models.data_access_object.RowDeletedException):
            pass

        # can throw exceptions if these credentials don't work
        auth = dao.new_auth(auth_class, provider_id, secret, user, expires_ts)
        dao.save(auth)

        session_dao = framework.models.session.SessionDAO()

        session = session_dao.new_session(auth, user_agent)
        session_dao.save(session)

        return session


class InvalidCredentialsException(AuthException):
    def __str__(self):
        return "Invalid Credentials"


class ProviderIdTakenException(AuthException):
    _found_auth = None

    def __init__(self, found_auth):
        self._found_auth = found_auth

    def __str__(self):
        return self._found_auth.provider_id + " is already taken"

    @property
    def auth(self):
        return self._found_auth
