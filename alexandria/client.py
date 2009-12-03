class ReallyDumbTerminal(object):
    
    def __init__(self, client_id):
        self.client_id = client_id
        self.store = {}
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    def display(self, msg):
        print self.format(msg, append ='')
    
    def read(self, msg=''):
        return raw_input(self.format(msg))
    


