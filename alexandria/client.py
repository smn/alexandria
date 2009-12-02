class ReallyDumbTerminal(object):
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    def display(self, msg):
        print self.format(msg, append ='')
    
    def read(self, msg=''):
        return raw_input(self.format(msg))
    


