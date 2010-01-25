from validators import always_true
from exceptions import InvalidInputException
from utils import msg, consumer

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.state = [
            prompt('what menu?')
        ]
        self.store = {}
    
    def clone(self, **kwargs):
        """Clone self, always return a clone instead of self when chaining
        methods, otherwise you'll get lost of confusing behaviour because
        vars are passed by reference"""
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__ = self.__dict__.copy()
        clone.__dict__.update(kwargs)
        return clone
    
    def do(self, *items):
        """Clone the state and append a batch of items to it"""
        clone = self.clone()
        clone.state.extend(list(items))
        return clone
    
    def run(self, start_at=0):
        cloned_state = self.state[start_at:]
        while cloned_state:
            # find out where we are in the stack
            current_step = len(self.state) - len(cloned_state)
            
            # we always expect an answer before we get a response
            incoming = (yield)
            print '>>> %s' % incoming
            
            try:
                # get last question for which we will now get an answer
                previous_coroutine = cloned_state[0]
                print 'previous_coroutine', previous_coroutine
                previous_coroutine.send(self) # send 'ms'
                print 'sent ms'
                previous_coroutine.send(incoming) # send 'answer'
                print 'sent incoming: %s' % incoming
                
                # we've answered the previous answer correctly, can be
                # removed from the state
                cloned_state.remove(previous_coroutine)
                print 'removed successful previous_coroutine'
                
                next_coroutine = cloned_state[0]
                print 'got next coroutine'
                next_question = next_coroutine.send(self) # send 'ms'
                print 'next question: %s' % next_question
                
                print 'yielding', current_step, next_coroutine, next_question
                yield current_step, next_coroutine, next_question
                print 'yielded'
            except InvalidInputException, e:
                print "repeating coroutine", previous_coroutine
                continue


@consumer
def prompt(text, validator=always_true, options=()):
    while True:
        # wait to be given the menu system instance
        ms = yield
        # read input from client and store it
        answer = yield msg(text, options)
        validated_answer = validator(answer, options)
        # initialize storage as a list if it doesn't exist
        ms.store.setdefault(text, [])
        ms.store[text].append(validated_answer)
        yield validated_answer


@consumer
def do(items):
    while True:
        # clone items for the next loop
        cloned_items = items[:]
        ms = (yield)
        while cloned_items:
            item = cloned_items[-1]
            result = item.send(ms)
            # only remove from the queue if we've gotten an answer, which means
            # it's been validated
            if result:
                cloned_items.remove(item)

@consumer
def display(message):
    while True:
        ms = (yield)
        yield message

