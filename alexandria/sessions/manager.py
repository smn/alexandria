from alexandria.dsl.core import coroutine
from generator_tools.copygenerators import copy_generator
import logging

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
    
    def get_previously_sent_item(self, menu_system):
        """
        Get the item that was previously sent to the client. It is needed to 
        be able to determine what question the incoming answer is answering.
        """
        previous_index = self.data.get('previous_index', None)
        # we can't check for just previous_index, since zero resolves to False 
        # in an if statement
        if previous_index >= 0:
            return copy_generator(menu_system.stack[previous_index - 1])
    
