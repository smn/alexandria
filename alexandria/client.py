from alexandria.core import coroutine
from alexandria.exceptions import InvalidInputException
import logging

class Client(object):
    
    def answer(self, answer, item, menu_system):
        item.next()
        question = item.send(menu_system)
        # question = item.next() # re-read the question asked
        item.next() # proceed to answer, feed manually
        return question, item.send(answer)
        
    def ask(self, item, menu_system):
        item.next()
        question = item.send(menu_system)
        return question, self.send(question)
    
    def step(self, current_item, next_item, menu_system):
        # receive answer and pass it to the last question that was asked
        answer = self.receive()
        try:
            if current_item:
                question, validated_answer = self.answer(answer, current_item, menu_system)
            else:
                logging.debug('no current item to answer to')
            
            if next_item:
                self.ask(next_item, menu_system)
            else:
                logging.debug('no next item to ask question, end of menu reached')
            
        except InvalidInputException, e:
            logging.exception(e)
            repeat_item = menu_system.repeat_current_item()
            repeat_item.next()
            repeated_question = repeat_item.send(menu_system)
            logging.debug('repeating current question: %s' % repeated_question)
            self.send(repeated_question)
    
    def do_step(self, step, menu_system):
        menu_system.fast_forward(step)
        self.step(*menu_system.next())
    
    def process(self, menu_system):
        for current_item, next_item in iter(menu_system):
            self.step(current_item, next_item, menu_system)

class FakeUSSDClient(Client):
    
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
    

