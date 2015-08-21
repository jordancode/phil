from framework.storage.mysql import MySQL
from framework.models.domain.authentication import (Authentication, AuthException)
from framework.models.domain.session import Session, SessionException
from framework.models.domain.user_agent import UserAgent
from framework.models.data_access.data_access_object import DataAccessObject, RowNotFoundException
from framework.models.data_access.auth_dao import AuthDAO
from app.models.data_access.user_dao import UserDAO
from framework.utils.id import Id

import hashlib

class SessionDAO(DataAccessObject):
    
    _user_agents = None
    
    def __init__(self):
        super().__init__(Session)
        self._user_agents = {}
        
        
    def new_session(self, auth, user_agent_string, log_out_ts = None, session_flags = None):
        
        user = auth.user
        new_session_id = MySQL.next_id(Id(user.id).get_shard_id())
        
        try:
            user_agent = self._get_user_agent_by_string(user_agent_string)
        except UserAgentNotFoundException:
            shard_id = MySQL.get_shard_id_for_string(user_agent_string)
            id = MySQL.next_id(shard_id)
            user_agent  = UserAgent(id, user_agent_string)
            self._save_user_agent(user_agent)
        
        return Session(new_session_id, user, user_agent, auth, log_out_ts=log_out_ts, flags=session_flags)
        
        
        
    def save(self, session):
        if session.is_dirty:
            session_dict = self._session_to_row(session)
            session_query = (
                    "INSERT INTO sessions VALUES("
                    "%(id)s, %(user_id)s, %(user_agent_id)s, %(auth_id)s, %(created_ts)s,"
                    " %(modified_ts)s, %(log_out_ts)s, NULL, %(flags)s, %(token)s"
                    ") ON DUPLICATE KEY UPDATE"
                    " user_agent_id=VALUES(user_agent_id), modified_ts=VALUES(modified_ts),"
                    " log_out_ts=VALUES(log_out_ts), flags=VALUES(flags)"
                )
            MySQL.get(session.id).query(session_query,session_dict)
            session.update_stored_state()

        
    def get_all_sessions_for_user(self, user):
        query = "SELECT * FROM sessions WHERE user_id=%s"
        shard = MySQL.get(user.id)
        rows = shard.query(query,(user.id))
        
        ret = []
        for row in rows:
            ret.append(self._row_to_session(row,user))
        
        return ret
        
        
    
    def get_active_sessions_for_user(self, user):
        query = "SELECT * FROM sessions WHERE user_id=%s AND (log_out_ts=NULL OR log_out_ts>NOW())"
        shard = MySQL.get(user.id)
        rows = shard.query(query,(user.id))
        
        ret = []
        for row in rows:
            ret.append(self._row_to_session(row,user))
        
        return ret
        
    def get_last_session_for_user(self, user):
        query = "SELECT * FROM sessions WHERE user_id=%s ORDER BY modified_ts DESC LIMIT 1"
        shard = MySQL.get(user.id)
        rows = shard.query(query,(user.id))
        
        if not len(rows):
            raise SessionNotFoundException()
        
        return self._row_to_session(rows[0],user)
     
     
    def get_last_active_session_for_user(self, user):
        query = "SELECT * FROM sessions WHERE user_id=%s AND (log_out_ts=NULL OR log_out_ts>NOW()) ORDER BY modified_ts DESC LIMIT 1"
        shard = MySQL.get(user.id)
        rows = shard.query(query,(user.id))
        
        if not len(rows):
            raise SessionNotFoundException()
        
        return self._row_to_session(rows[0],user)
        
    
    def get_session(self, session_id):
        
        shard = MySQL.get(session_id)
        
        rows = shard.query("SELECT * FROM sessions WHERE id=%s",(session_id))
        
        if not len(rows):
            raise SessionNotFoundException()
        
        return self._row_to_session(rows[0])
    
    
    def _get_user_agent_by_string(self, user_agent_string):
        shard_id = MySQL.get_shard_id_for_string(user_agent_string)
        hash = UserAgent.generate_hash(user_agent_string)
        
        
        rows = MySQL.get_by_shard_id(shard_id).query("SELECT * FROM user_agents WHERE user_agent_hash = %s", (hash,))
        
        if not len(rows):
            raise UserAgentNotFoundException()
        
        row = rows[0]
        
        if row['id'] not in self._user_agents:
            self._user_agents[row['id']] = UserAgent(row['id'],row['user_agent_string'].decode("utf-8"))
            
        return self._user_agents[row['id']]
        
    
    def _get_user_agent_by_id(self, user_agent_id):
        if user_agent_id not in self._user_agents:
            rows = MySQL.get(user_agent_id).query("SELECT * FROM user_agents WHERE id = %s", (user_agent_id))
            if not len(rows):
                raise UserAgentNotFoundException()
            
            row = rows[0]
            self._user_agents[user_agent_id] = UserAgent(row['id'],row['user_agent_string'].decode("utf-8"))
            
        return self._user_agents[user_agent_id]

    def _save_user_agent(self,user_agent):
        if user_agent.is_dirty:
            ua_dict = user_agent.to_dict()
            ua_query = "INSERT IGNORE INTO user_agents VALUES(%(id)s, %(hash)s, %(string)s, NOW())"
            MySQL.get(user_agent.id).query(ua_query, ua_dict)
            user_agent.update_stored_state()
                
    
    def _row_to_session(self,row, user = None):  
        ua = self._get_user_agent_by_id(row['user_agent_id'])
        
        if user is None:
            user_dao = UserDAO()
            user = user_dao.get_user_by_id(row['user_id'])
            
        auth_dao = AuthenticationDAO()
        auth = auth_dao.get_auth_by_id(row['auth_id'])
        
        sesh = Session(row['id'],user,ua,auth,row['created_ts'],row['modified_ts'],row['log_out_ts'],row['flags'])
        sesh.update_stored_state()
        
        return sesh
    
    def _session_to_row(self, session):
        dict = session.to_dict()
        return {
                "id" : session.id,
                "user_id" : session.user.id,
                "auth_id" : session.auth.id,
                "user_agent_id" : session.user_agent.id,
                "created_ts" : dict['created_ts'],
                "modified_ts" : dict['modified_ts'],
                "log_out_ts" : dict['log_out_ts'],
                "flags" : dict['flags'],
                "token" : dict['token']
                }
    

class UserAgentNotFoundException(RowNotFoundException, SessionException):
    def __str__(self):
        return "User Agent not found"
    
class SessionNotFoundException(RowNotFoundException, SessionException):
    def __str__(self):
        return "Session row not found"
    
    
    