class SessionManager(object):
    """
    The state of a client connecting to the system. 
    
    FIXME: this design is prone to race conditions
    """
    
    def __init__(self, client, backend):
        self.client = client
        self.backend = backend
    
    def restore(self):
        """
        Restore the current state from the backend
        """
        self.data = self.backend.restore(self.client)
    
    def save(self, deactivate=False):
        """
        Save the current state to the backend. Specify deactivate=True if you
        want to close this session for good.
        """
        self.backend.save(self.client, self.data)
        if deactivate:
            self.backend.deactivate(self.client)
    
