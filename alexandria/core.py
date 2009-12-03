from validators import always_true
from exceptions import InvalidInputException
from utils import msg

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.state = []
    
    def do(self, *items):
        """Append a batch of items to the state"""
        [self.state.append(item) for item in list(items)]
        return self
    
    def run(self, client, start_at=0):
        self.client = client
        # work on a cloned state so original state is untouched and we
        # can always continue from where we left off previously
        cloned_state = self.state[start_at:]
        while cloned_state:
            current_step = len(self.state) - len(cloned_state)
            routine = cloned_state[0]
            result = routine.invoke().send(self)
            if result:
                cloned_state.remove(routine)
                yield (current_step, routine)
    

def coroutine(func): 
    def start(*args,**kwargs): 
        cr = func(*args,**kwargs) 
        cr.next() 
        return cr 
    return start 


class DelayedCall(object):
    """FIXME: This is a solution to a lower problem that hasn't been adressed yet"""
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    def __str__(self):
        return 'DelayedCall(%s)' % self.__dict__
    
    def invoke(self):
        return self.fn(*self.args, **self.kwargs)
    


def delay_call(fn):
    """Wrap the call to the function in a DelayedCall, not sure if I want 
    to keep this. The main reason is that DelayedCalls are easier to introspect
    than coroutine generators. I'd like to know something about the coroutine
    I'm starting before it runs"""
    def wrapper(*args, **kwargs):
        return DelayedCall(fn,*args, **kwargs)
    return wrapper


@delay_call
@coroutine
def prompt(text, validator=always_true, options=()):
    while True:
        # wait to be given the menu system instance
        ms = (yield)
        # initialize storage as a list if it doesn't exist
        ms.client.store.setdefault(text, [])
        # read input from client and store it
        answer = ms.client.read(msg(text, options))
        try:
            validated_answer = validator(answer, options)
            ms.client.store[text].append(validated_answer)
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
        ms.client.display(message)
        yield True

