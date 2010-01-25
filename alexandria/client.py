from alexandria.core import consumer
from alexandria.exceptions import InvalidInputException

class FakeUSSDClient(object):
    
    def __init__(self, client_id):
        """
        Should go something like so:
        
        >>> from collections import namedtuple
        >>> Menu = namedtuple('Menu',['question','answer'])
        >>> menu = Menu._make('What is your name?', '')
        >>> fuc = FakeUSSDClient('1')
        >>> fuc.send(menu)
        -> what is your name?
        <- Simon
        >>> m.answer
        'Simon'
        
        """
        self.client_id = client_id
        self.response = ''
    
    def receive(self):
        return self.response
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    def send(self, text):
        self.response = raw_input(self.format(text))
    

