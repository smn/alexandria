from alexandria.core import coroutine
from alexandria.exceptions import InvalidInputException
from generator_tools.copygenerators import copy_generator
from alexandria.backend import DBBackend, InMemoryBackend
import logging

# store state in client
# serialize state only
# state has slots for previous question (pending an answer)
# answer always fills in the slot - allows us to skip questions that
# appear to be irrelevant as we progress through the menu


class State(object):
    
    def __init__(self, client):
        self.client = client
        self.backend = DBBackend(client)
    
    def restore(self):
        self.data = self.backend.restore()
    
    def save(self, deactivate=False):
        self.backend.save(self.data)
        if deactivate:
            self.backend.deactivate()
    
    def get_previously_sent_item(self, menu_system):
        previous_index = self.data.get('previous_index', None)
        # we can't check for just previous_index, since zero resolves to False 
        # in an if statement
        if previous_index >= 0:
            return copy_generator(menu_system.stack[previous_index - 1])
    
    def next(self, answer, menu_system):
        # check what item was sent previously
        try:
            item_awaiting_answer = self.get_previously_sent_item(menu_system)
            # print "data, checking for answer: ", self.data
            if item_awaiting_answer:
                # if this is the case it means we're at the start of a session
                # with a client. We're assuming that the client always initiates
                # the conversation - which is the case with USSD
                
                item_awaiting_answer.next()
                question, end_session = item_awaiting_answer.send((menu_system, self.data))
                # print 'answering: %s with %s' % (question[0:20], answer)
                item_awaiting_answer.next() # proceed to answer, feed manually
                validated_answer = item_awaiting_answer.send(answer)
                # print 'validated answer', answer
            else:
                logging.debug('client initiated contact with: %s' % answer)
        
            ###### SEND OUTPUT
            index, item = menu_system.next_after(self.data.get('previous_index',0))
            while item:
                # start coroutine
                item.next()
                # send the menu system, yields the question
                question, end_session = item.send((menu_system, self.data)) 
                # coroutines may return empty or False values which means they have
                # nothing to ask the client
                if question:
                    self.client.send(question, end_session)
                    # print 'setting previous index to', index
                    self.data['previous_index'] = index
                    break # break out of ugly while True: loop
                else:
                    index, item = menu_system.next()
            
        except InvalidInputException, e:
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
    

