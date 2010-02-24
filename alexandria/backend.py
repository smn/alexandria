
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

class DjangoBackend(object):
    
    def __init__(self):
        from django.conf import settings
        from alexandria.backends.django import settings
        settings.configure(deault_settings=settings)
        from alexandria.backends.django.models import Client
    
    def restore(self, client):
        client = Client.objects.get(uuid=client.id)
        return dict([(item.key, item.value) for item in client.item_set.all()])
    
    def save(self, client, state):
        client = Client.objects.create(uuid=client.id)
        for key, value in state.items():
            client.item_set.create(key=key, value=value)
        return state