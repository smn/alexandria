from alexandria.core import coroutine
from alexandria.exceptions import InvalidInputException
from generator_tools.copygenerators import copy_generator
import logging

# store state in client
# serialize state only
# state has slots for previous question (pending an answer)
# answer always fills in the slot - allows us to skip questions that
# appear to be irrelevant as we progress through the menu

class Client(object):
    
    def __init__(self, client_id):
        self.state = {
            "expecting": None,
        }
        self.client_id = client_id
        self.response = ''
    
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
    
    def get_previously_sent_item(self, menu_system):
        previous_index = self.state['expecting']
        # we can't check for just previous_index, since zero resolves to False 
        # in an if statement
        if previous_index >= 0: 
            return copy_generator(menu_system.stack[previous_index])
    
    def step(self, index, item, menu_system):
        # receive answer and pass it to the last question that was asked
        
        # drop current, next iterator
        # go for only next iterator
        # keep track of last item
        # answer back to last item
        # provide next item
        # items that do nothing should yield False
        
        ##### RECEIVE INPUT
        
        # to make this non-blocking this will probably need to go elsewhere
        answer = self.receive()
        
        # check what item was sent previously
        try:
            item_awaiting_answer = self.get_previously_sent_item(menu_system)
            if item_awaiting_answer:
                # if this is the case it means we're at the start of a session
                # with a client. We're assuming that the client always initiates
                # the conversation - which is the case with USSD
            
                question, validated_answer = \
                            self.answer(answer, item_awaiting_answer, menu_system)
            else:
                logging.debug('client initiated contact with: %s' % answer)
        
            ###### SEND OUTPUT
        
            while item:
                # iterate
                # index, item = menu_system.next()
            
                # start coroutine
                item.next() 
                # send the menu system, yields the question
                question = item.send(menu_system) 
                # coroutines may return empty or False values which means they have
                # nothing to ask the client
                if question: 
                    self.send(question)
                    self.state['expecting'] = index
                    break # break out of ugly while True: loop
                else:
                    index, item = menu_system.next()
                
        except InvalidInputException, e:
            logging.exception(e)
            index, repeat_item = menu_system.repeat_current_item()
            repeat_item.next()
            repeated_question = repeat_item.send(menu_system)
            self.state['expecting'] = index
            logging.debug('repeating current question: %s' % repeated_question)
            self.send(repeated_question)
            
        # try:
        #     
        #     if item_awaiting_answer:
        #         question, validated_answer = self.answer(answer, item_awaiting_answer, menu_system)
        #     else:
        #         logging.debug('no current item to answer to')
        #     
        #     if next_item:
        #         # self.ask(next_item, menu_system)
        #         while True:
        #             index, current_item, next_item = menu_system.next()
        #             next_item.next()
        #             question = next_item.send(menu_system)
        #             if question:
        #                 self.send(question)
        #                 self.state['expecting'] = index # keep track of what question
        #                                                 # was asked last
        #                 break
        #     else:
        #         logging.debug('no next item to ask question, end of menu reached')
        #     
        # except InvalidInputException, e:
        #     logging.exception(e)
        #     repeat_item = menu_system.repeat_current_item()
        #     repeat_item.next()
        #     repeated_question = repeat_item.send(menu_system)
        #     logging.debug('repeating current question: %s' % repeated_question)
        #     self.send(repeated_question)
    
    def do_step(self, step, menu_system):
        menu_system.fast_forward(step)
        self.step(*menu_system.next())
    
    def process(self, menu_system):
        for index, item in iter(menu_system):
            self.step(index, item, menu_system)

class FakeUSSDClient(Client):
    
    def connect(self, menu_system):
        pass
    
    def receive(self):
        return raw_input('<- ')
    
    def format(self, msg):
        return '-> ' + '\n-> '.join(msg.split('\n'))
    
    def send(self, text):
        print self.format(text)
    

