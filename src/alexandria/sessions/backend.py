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
    
    def restore(self, alexandria_client):
        """
        Restore the current client's session from the database by creating a
        dictionary from the deserialized key/value pairs
        """
        client = Client.objects.recent(**alexandria_client.uuid())
        session = dict([(item.key, item.deserialized_value) for item in \
                                                    client.item_set.all()])
        session.update({
            'msisdn': alexandria_client.id
        })
        return session
    
    def deactivate(self, alexandria_client):
        """
        Deactivate the client, happens when the session's been completed. 
        Makes sure that when the client reconnects a new session starts
        instead of continuing with a completed one.
        """
        client = Client.objects.recent(**alexandria_client.uuid())
        client.active = False
        client.save()
    
    def save(self, alexandria_client, state):
        """
        Serialize the state for the given client to the database, the state
        is a dictionary with key/value pairs.
        """
        client = Client.objects.recent(**alexandria_client.uuid())
        for key, value in state.items():
            try:
                item = client.item_set.get(key=key)
                item.value = value
                item.save()
            except Item.DoesNotExist, e:
                client.item_set.create(key=key, value=value)
        return state