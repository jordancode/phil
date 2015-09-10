class BaseSessionStore:
    """
      interface for storing and retrieving session ids to and from the client
    """
    
    def set_session(self, response, session):
        pass
    
    def get_session(self, request):
        pass
    
    def delete_session(self, response):
        pass;