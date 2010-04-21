
class InMemoryBackend(object):
    """
    An in memory backend that stores data in a very ugly global
    variable. NEVER use this in a production environment.
    """
    def __init__(self):
        globals().setdefault('ALEXANDRIA_GLOBAL_STATE',{})
    
    def restore(self, client):
        global ALEXANDRIA_GLOBAL_STATE
        return ALEXANDRIA_GLOBAL_STATE.setdefault(client.id, {})
    
    def save(self, client, state):
        global ALEXANDRIA_GLOBAL_STATE
        ALEXANDRIA_GLOBAL_STATE[client.id] = state


# FIXME:    This is django ugliness, we should either choose to make the whole
#           thing a Django app or we should remove the dependency entirely
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'alexandria.sessions.db.settings'

from django.conf import settings
from alexandria.sessions.db.models import Client, Item

class DBBackend(object):
    """
    A database backend. Stores all session data in a database through the 
    Django ORM. It does this by serializing data as best it can. It's ugly but
    it works, we need something more pluggable and elegant.
    """
    def __init__(self, client):
        # get a recent client, recent is a client that has connected within
        # the last three minutes
        self.client = Client.objects.recent(uuid=client.id, 
                                        client_type=client.__class__.__name__)
    
    def restore(self):
        """
        Restore the current client's session from the database by creating a
        dictionary from the deserialized key/value pairs
        """
        return dict([(item.key, item.deserialized_value) for item in \
                                                self.client.item_set.all()])
    
    def deactivate(self):
        """
        Deactivate the client, happens when the session's been completed. 
        Makes sure that when the client reconnects a new session starts
        instead of continuing with a completed one.
        """
        self.client.active = False
        self.client.save()
    
    def save(self, state):
        """
        Serialize the state for the given client to the database, the state
        is a dictionary with key/value pairs.
        """
        for key, value in state.items():
            try:
                item = self.client.item_set.get(key=key)
                item.value = value
                item.save()
            except Item.DoesNotExist, e:
                self.client.item_set.create(key=key, value=value)
        return state