from statemachine import StateMachine
import random

class ReallyDumbTerminal(object):
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    def display(self, msg):
        print self.format(msg, append ='')
    
    def read(self, msg=''):
        return raw_input(self.format(msg))
    


class MenuSystem(object):
    def __init__(self):
        self.state = []
        self.recorded_routines = {}
        self.store = {}
    
    def do(self, *items):
        self.state.append(do(list(items)))
        return self
    
    def continue_if(self, fn):
        self.state.append(continue_if(fn))
        return self
    
    def dump_state(self):
        for idx, routine in enumerate(self.state):
            print idx, routine.__name__
        return self
    
    def dump_store(self):
        for key, value in self.store.items():
            print 'key:', key, 'value:', value
        return self
    
    def run(self, client):
        self.client = client
        [routine.send(self) for routine in self.state]
        return self


# from http://www.dabeaz.com/coroutines/Coroutines.pdf
def coroutine(func): 
    def start(*args,**kwargs): 
        cr = func(*args,**kwargs) 
        cr.next() 
        return cr 
    return start 

@coroutine
def prompt(message):
    while True:
        # wait to be given the menu system instance
        ms = (yield)
        # initialize storage as a list if it doesn't exist
        ms.store.setdefault(message, [])
        # read input from client and store it
        ms.store[message].append(ms.client.read(message))

@coroutine
def loop(*items, **kwargs):
    items = list(items)
    if 'random' in kwargs: random.shuffle(items)
    while True:
        ms = (yield)
        while items:
            item = items.pop()
            item.send(ms)

@coroutine
def do(items):
    while True:
        # clone items for the next loop
        cloned_items = items[:]
        # We're popping, which means we need to reverse the order because
        # otherwise we'll get the items back to front
        cloned_items.reverse()
        ms = (yield)
        while cloned_items:
            item = cloned_items.pop()
            item.send(ms)

@coroutine
def display(message):
    while True:
        ms = (yield)
        ms.client.display(message)

@coroutine
def testing_a_callback(*args, **kwargs):
    while True:
        ms = (yield)
        ms.client.display('hello from callback: %s, %s' % (args, kwargs))

@coroutine
def inbox():
    while True:
        ms = (yield)
        ms.prompt('Are you really %s?' % ms.answers['What is your name?'])
        ms.prompt('Yay or nay?')



def ol(list):
    """ordered list"""
    return '\n'.join('%s: %s' % (idx, item) for idx,item in enumerate(list))

# ms = MenuSystem()
# ms \
#     .prompt('What is your name?') \
#     .loop(
#         prompt('How old are you?'),
#         prompt('What is your favorite food?'),
#         prompt('What is your favorite colour?'),
#         randomize=True
#     ) \
#     .mark('show inbox',
#         prompt('This is your inbox:\n%s' % ol([
#             'Message 1',
#             'Message 2',
#             'Message 3',
#         ]))
#     ) \
#     .display('Thank you, goodbye') \
#     .do('show inbox') \
#     .append(testing_a_callback('a','b')) \
#     .append(inbox()) \
#     .run(client=ReallyDumbTerminal()) \
#     .dump_store()

get_personal_info = [
    prompt('What is your name?'),
    prompt('What is your age?'), 
    prompt('Where do you live?')
]

show_inbox = [
    prompt('This is your inbox:\n%s' % ol([
        'Message 1',
        'Message 2',
        'Message 3',
    ]))
]

def completed_personal_info(ms):
    questions = [
        'What is your name?',
        'What is your age?',
        'Where do you live?'
    ]
    # kludgy
    answers = [(ms.store.get(q) != ['']) for q in questions]
    return all(answers)

ms = MenuSystem()
ms \
    .do(*get_personal_info) \
    .do(*show_inbox) \
    .do(
        loop(
            prompt('How old are you?'),
            prompt('What is your favorite food?'),
            prompt('What is your favorite colour?'),
            random=True
        )
    ) \
    .run(client=ReallyDumbTerminal()) \
    .dump_store()

