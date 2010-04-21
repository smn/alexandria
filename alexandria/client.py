from alexandria.dsl.core import coroutine
from alexandria.dsl.exceptions import InvalidInputException
from generator_tools.copygenerators import copy_generator
from alexandria.sessions.backend import DBBackend, InMemoryBackend
import logging


class State(object):
    """
    The state of a client connecting to the system. 
    
    FIXME: This should be in it's own module
    """
    
    def __init__(self, client):
        self.client = client
        # FIXME:    the backend should be pluggable from settings, not so 
        #           deep down in the code
        self.backend = DBBackend(client)
    
    def restore(self):
        """
        Restore the current state from the backend
        
        FIXME:  This is hideous, we should be providing the backend with some
                client vars with which it should be able to return the state,
                passing along the the whole client at __init__ is ugly.
        """
        self.data = self.backend.restore()
    
    def save(self, deactivate=False):
        """
        Save the current state to the backend. Specify deactivate=True if you
        want to close this session for good.
        """
        self.backend.save(self.data)
        if deactivate:
            self.backend.deactivate()
    
    def get_previously_sent_item(self, menu_system):
        """
        Get the item that was previously sent to the client. It is needed to 
        be able to determine what question the incoming answer is answering.
        """
        previous_index = self.data.get('previous_index', None)
        # we can't check for just previous_index, since zero resolves to False 
        # in an if statement
        if previous_index >= 0:
            return copy_generator(menu_system.stack[previous_index - 1])
    
    def next(self, answer, menu_system):
        """
        Step through the system, go to the next item. The answer is the incoming
        input coming from the client.
        """
        # check what item was sent previously
        try:
            item_awaiting_answer = self.get_previously_sent_item(menu_system)
            if item_awaiting_answer:
                # if we have an item_awaiting_answer then it means this is a
                # returning session. The incoming answer is an answer to a
                # question we've sent earlier.
                item_awaiting_answer.next()
                question, end_session = item_awaiting_answer.send((menu_system, self.data))
                item_awaiting_answer.next() # proceed to answer, feed manually
                validated_answer = item_awaiting_answer.send(answer)
            else:
                # if this is the case it means we're not at the start of a session
                # with a client. We're assuming that the client always initiates
                # the conversation - which is the case with USSD
                logging.debug('client initiated contact with: %s' % answer)
        
            # send output back to the client
            index, item = menu_system.next_after(self.data.get('previous_index',0))
            while item:
                # We loop over the item's since they might not return a question
                # which means we have to move forward to the next time. Basically
                # we're looping over items until one returns a question to
                # send back to the client
                
                # FIXME: start coroutine, this can be automated with a @decorator
                item.next()
                # send the menu system, yields the question
                question, end_session = item.send((menu_system, self.data)) 
                # coroutines may return empty or False values which means they have
                # nothing to ask the client
                if question:
                    self.client.send(question, end_session)
                    self.data['previous_index'] = index
                    break # break out of ugly `while True:..` loop
                else:
                    index, item = menu_system.next()
            
        except InvalidInputException, e:
            # Invalid input exceptions can be raised which means the client didn't 
            # provide correct input for the given question. If that's the case
            # then we ask the question again.
            logging.exception(e)
            index, repeat_item = menu_system.repeat_current_item()
            repeat_item.next()
            repeated_question, end_session = repeat_item.send((menu_system, self.data))
            self.data['previous_index'] = index
            logging.debug('repeating current question: %s' % repeated_question)
            self.client.send(repeated_question, end_session)
            


class Client(object):
    def __init__(self, id):
        self.id = id
        self.state = State(client=self)
        self.state.restore()
    
    def answer(self, message, menu_system):
        self.state.restore()
        self.state.next(message, menu_system)
        self.state.save()
    
    def deactivate(self):
        self.state.save(deactivate=True)


class FakeUSSDClient(Client):
    def receive(self):
        return raw_input('<- ')
    
    def format(self, msg):
        return '-> ' + '\n-> '.join(msg.split('\n'))
    
    def send(self, text, end_session):
        print self.format(text)
        if end_session:
            self.deactivate()
            print 'end of menu'
    

