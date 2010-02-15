global GLOBAL_STATE
GLOBAL_STATE = {}

class InMemoryBackend(object):
    
    def __init__(self):
        pass
    
    def restore(self, client):
        global GLOBAL_STATE
        return GLOBAL_STATE.setdefault(client.id, {})
    
    def save(self, client, state):
        global GLOBAL_STATE
        GLOBAL_STATE[client.id] = state
        