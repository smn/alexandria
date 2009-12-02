from validators import always_true
from exceptions import InvalidInputException
from utils import msg

class MenuSystem(object):
    def __init__(self):
        self.state = []
        self.recorded_routines = {}
        self.store = {}
    
    def do(self, *items, **kwargs):
        self.state.append(do(list(items), **kwargs))
        return self
    
    def dump_state(self):
        for idx, routine in enumerate(self.state):
            print idx, routine.__name__
        return self
    
    def dump_store(self):
        print "\n"
        print "=" * 60
        print "| View of current state".ljust(59) + '|'
        print "=" * 60
        longest_key = max([len(key) for key in self.store])
        for key, value in self.store.items():
            print key.ljust(longest_key + 2), ' => ', value
        print "\n"
        return self
    
    def run(self, client):
        self.client = client
        [routine.send(self) for routine in self.state]
        return self
    

def coroutine(func): 
    def start(*args,**kwargs): 
        cr = func(*args,**kwargs) 
        cr.next() 
        return cr 
    return start 

@coroutine
def prompt(text, validator=always_true, options=()):
    while True:
        # wait to be given the menu system instance
        ms = (yield)
        # initialize storage as a list if it doesn't exist
        ms.store.setdefault(text, [])
        # read input from client and store it
        answer = ms.client.read(msg(text, options))
        try:
            validated_answer = validator(answer, options)
            ms.store[text].append(validated_answer)
            yield validated_answer
        except InvalidInputException, e:
            print 'Invalid input received', e

@coroutine
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

@coroutine
def display(message):
    while True:
        ms = (yield)
        ms.client.display(message)


