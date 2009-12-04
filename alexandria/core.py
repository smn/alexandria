from validators import always_true
from exceptions import InvalidInputException
from utils import msg, consumer

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.state = []
        self.store = {}
    
    def do(self, *items):
        """Append a batch of items to the state"""
        self.state.extend(list(items))
        return self
    
    def run(self, start_at=0):
        cloned_state = self.state[start_at:]
        while cloned_state:
            current_step = len(self.state) - len(cloned_state)
            coroutine = cloned_state[0]
            output = coroutine.send(self)
            try:
                yield current_step, coroutine, output
                cloned_state.remove(coroutine)
            except InvalidInputException, e:
                print "repeating coroutine", coroutine
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

