
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
    
    def __init__(self, client):
        self.client = Client.objects.recent(uuid=client.id, 
                                            client_type=client.__class__.__name__)
    
    def restore(self):
        return dict([(item.key, item.deserialized_value) for item in self.client.item_set.all()])
    
    def deactivate(self):
        self.client.active = False
        self.client.save()
    
    def save(self, state):
        for key, value in state.items():
            try:
                item = self.client.item_set.get(key=key)
                item.value = value
                item.save()
            except Item.DoesNotExist, e:
                self.client.item_set.create(key=key, value=value)
        return state