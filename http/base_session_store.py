class BaseSessionStore:
    """
      interface for storing and retreiving session ids to and from the client
    """
    
    def set_session(self, response, session):
        pass
    
    def get_session(self, request):
        pass
    
    def log_out_session(self, response, session):
        pass;