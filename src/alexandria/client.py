from alexandria.dsl.exceptions import InvalidInputException
from generator_tools.copygenerators import copy_generator
import logging

class Client(object):
    def __init__(self, id, session_manager):
        self.id = id
        self.session_manager = session_manager
        self.session_manager.restore()
    
    def uuid(self):
        return {"uuid": self.id, "client_type": self.__class__.__name__}
    
    def get_previously_sent_item(self, menu_system):
        """
        Get the item that was previously sent to the client. It is needed to 
        be able to determine what question the incoming answer is answering.
        """
        previous_index = self.session_manager.data.get('previous_index', None)
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
        end_session = True
        try:
            item_awaiting_answer = self.get_previously_sent_item(menu_system)
            if item_awaiting_answer:
                # if we have an item_awaiting_answer then it means this is a
                # returning session. The incoming answer is an answer to a
                # question we've sent earlier.
                item_awaiting_answer.next()
                question, end_session = item_awaiting_answer.send((menu_system, self.session_manager.data))
                item_awaiting_answer.next() # proceed to answer, feed manually
                validated_answer = item_awaiting_answer.send(answer)
            else:
                # if this is the case it means we're not at the start of a session
                # with a client. We're assuming that the client always initiates
                # the conversation - which is the case with USSD
                logging.debug('client initiated contact with: %s' % answer)
            
            # send output back to the client
            index, item = menu_system.next_after(self.session_manager.data.get('previous_index',0))
            while item:
                # We loop over the item's since they might not return a question
                # which means we have to move forward to the next time. Basically
                # we're looping over items until one returns a question to
                # send back to the client

                # FIXME: start coroutine, this can be automated with a @decorator
                item.next()
                # send the menu system, yields the question
                question, end_session = item.send((menu_system, self.session_manager.data)) 
                # coroutines may return empty or False values which means they have
                # nothing to ask the client
                if question:
                    self.send(question, end_session)
                    self.session_manager.data['previous_index'] = index
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
            repeated_question, end_session = repeat_item.send((menu_system, self.session_manager.data))
            self.session_manager.data['previous_index'] = index
            logging.debug('repeating current question: %s' % repeated_question)
            self.send(repeated_question, end_session)
        finally:
            self.save_state(end_session)
    
    def send(self, message, end_of_session):
        raise NotImplementedError, "needs to be subclassed"
    
    def answer(self, message, menu_system):
        self.session_manager.restore()
        self.next(message, menu_system)
        # self.session_manager.save()
    
    def save_state(self, eom):
        self.session_manager.save(deactivate=eom)
    
    def deactivate(self):
        self.session_manager.save(deactivate=True)


class FakeUSSDClient(Client):
    def receive(self):
        return raw_input('<- ')
    
    def format(self, msg):
        return '-> ' + '\n-> '.join(msg.split('\n'))
    
    def send(self, text, end_session):
        print self.format(text)
        if end_session:
            self.deactivate()
            import sys
            sys.exit(0)
    

