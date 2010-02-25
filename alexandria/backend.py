
class InMemoryBackend(object):
    
    def __init__(self):
        globals().setdefault('ALEXANDRIA_GLOBAL_STATE',{})
    
    def restore(self, client):
        global ALEXANDRIA_GLOBAL_STATE
        return ALEXANDRIA_GLOBAL_STATE.setdefault(client.id, {})
    
    def save(self, client, state):
        global ALEXANDRIA_GLOBAL_STATE
        ALEXANDRIA_GLOBAL_STATE[client.id] = state


import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'alexandria.backends.db.settings'

from django.conf import settings
from alexandria.backends.db.models import Client, Item

class DBBackend(object):
    
    def restore(self, client):
        try:
            client = Client.objects.recent(uuid=client.id, client_type=client.__class__.__name__)
            return dict([(item.key, item.deserialized_value) for item in client.item_set.all()])
        except Client.DoesNotExist, e:
            return {}
    
    def save(self, client, state):
        client = Client.objects.recent(uuid=client.id, client_type=client.__class__.__name__)
        for key, value in state.items():
            try:
                item = client.item_set.get(key=key)
                item.value = value
                item.save()
            except Item.DoesNotExist, e:
                client.item_set.create(key=key, value=value)
        return state