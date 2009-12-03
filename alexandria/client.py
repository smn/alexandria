from alexandria.core import coroutine
class ReallyDumbTerminal(object):
    
    def __init__(self, client_id):
        self.client_id = client_id
        self.store = {}
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    @coroutine
    def display(self, msg):
        while True:
            msg = (yield)
            print self.format(msg, append ='')
            yield ''
    
    @coroutine
    def read(self):
        while True:
            msg = (yield)
            yield raw_input(self.format(msg))
    


