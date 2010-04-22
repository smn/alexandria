from alexandria.dsl.exceptions import InvalidInputException
from alexandria.sessions.manager import SessionManager
from alexandria.sessions.backend import DBBackend
import logging

class Client(object):
    def __init__(self, id):
        self.id = id
        self.session = SessionManager(client=self, backend=DBBackend())
        self.session.restore()
    
    def uuid(self):
        return {"uuid": self.id, "client_type": self.__class__.__name__}
    
    def next(self, answer, menu_system):
        """
        Step through the system, go to the next item. The answer is the incoming
        input coming from the client.
        """
        # check what item was sent previously
        try:
            item_awaiting_answer = self.session.get_previously_sent_item(menu_system)
            if item_awaiting_answer:
                # if we have an item_awaiting_answer then it means this is a
                # returning session. The incoming answer is an answer to a
                # question we've sent earlier.
                item_awaiting_answer.next()
                question, end_session = item_awaiting_answer.send((menu_system, self.session.data))
                item_awaiting_answer.next() # proceed to answer, feed manually
                validated_answer = item_awaiting_answer.send(answer)
            else:
                # if this is the case it means we're not at the start of a session
                # with a client. We're assuming that the client always initiates
                # the conversation - which is the case with USSD
                logging.debug('client initiated contact with: %s' % answer)
            
            # send output back to the client
            index, item = menu_system.next_after(self.session.data.get('previous_index',0))
            while item:
                # We loop over the item's since they might not return a question
                # which means we have to move forward to the next time. Basically
                # we're looping over items until one returns a question to
                # send back to the client

                # FIXME: start coroutine, this can be automated with a @decorator
                item.next()
                # send the menu system, yields the question
                question, end_session = item.send((menu_system, self.session.data)) 
                # coroutines may return empty or False values which means they have
                # nothing to ask the client
                if question:
                    self.send(question, end_session)
                    self.session.data['previous_index'] = index
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
            repeated_question, end_session = repeat_item.send((menu_system, self.session.data))
            self.session.data['previous_index'] = index
            logging.debug('repeating current question: %s' % repeated_question)
            self.send(repeated_question, end_session)
    
    def send(self, message, end_of_session):
        raise NotImplementedError, "needs to be subclassed"
    
    def answer(self, message, menu_system):
        self.session.restore()
        self.next(message, menu_system)
        self.session.save()
    
    def deactivate(self):
        self.session.save(deactivate=True)


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
    

