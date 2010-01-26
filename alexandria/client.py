from alexandria.core import coroutine
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
    
    def connect(self, menu_system):
        pass
    
    def receive(self):
        return raw_input('<- ')
    
    def format(self, msg):
        return '-> ' + '\n-> '.join(msg.split('\n'))
    
    def send(self, text):
        print self.format(text)
    

