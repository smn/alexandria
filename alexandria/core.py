from validators import always_true
from exceptions import InvalidInputException
from utils import msg, coroutine, delay_call

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.state = []
        self.store = {}
    
    def do(self, *items):
        """Append a batch of items to the state"""
        self.state.extend(list(items))
        return self
    
    @coroutine
    def run(self, start_at=0):
        # work on a cloned state so original state is untouched and we
        # can always continue from where we left off previously
        cloned_state = self.state[start_at:]
        while cloned_state:
            # calculate the current step
            current_step = len(self.state) - len(cloned_state)
            # get the delayed call object
            delayed_call = cloned_state[0]
            # get the coroutine by invoking the delayed call
            coroutine = delayed_call.invoke()
            # get the output from the coroutine
            output = coroutine.send(self)
            # yield the output to the client, wait for the input to return
            input = (yield current_step, coroutine, output)
            if input:
                # remove from the cloned state so we continue with the next
                # entry next time around
                cloned_state.remove(delayed_call)
    


@delay_call
@coroutine
def prompt(text, validator=always_true, options=()):
    while True:
        # wait to be given the menu system instance
        ms = (yield)
        # initialize storage as a list if it doesn't exist
        ms.store.setdefault(text, [])
        # read input from client and store it
        answer = (yield msg(text, options))
        try:
            validated_answer = validator(answer, options)
            ms.store[text].append(validated_answer)
            yield validated_answer
        except InvalidInputException, e:
            print 'Invalid input received', e


@delay_call
@coroutine
def do(items):
    while True:
        # clone items for the next loop
        cloned_items = items[:]
        ms = (yield)
        while cloned_items:
            item = cloned_items[-1]
            result = item.invoke().send(ms)
            # only remove from the queue if we've gotten an answer, which means
            # it's been validated
            if result:
                cloned_items.remove(item)

@delay_call
@coroutine
def display(message):
    while True:
        ms = (yield)
        yield message

