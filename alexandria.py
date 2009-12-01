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
        self.answers = {}
    
    def store(self, key, value):
        self.answers[key] = value
        return value
    
    def append(self, routine):
        self.state.append(routine)
        return self
    
    def prompt(self, msg):
        self.state.append(prompt(msg))
        return self
    
    def display(self, msg):
        self.state.append(display(msg))
        return self
    
    def loop(self, *items, **kwargs):
        self.state.append(loop(list(items), **kwargs))
        return self
    
    def dump_store(self):
        for key, value in self.answers.items():
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
        ms = (yield)                                # wait to be given the menu system instance
        ms.store(message, ms.client.read(message))  # read input from client and yield it back


@coroutine
def loop(items, randomize=False):
    while True:
        ms = (yield)
        while items:
            # randomize order
            if randomize: random.shuffle(items)
            item = items.pop()
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

ms = MenuSystem()
ms \
    .prompt('What is your name?') \
    .loop(
        prompt('How old are you?'),
        prompt('What is your favorite food?'),
        prompt('What is your favorite colour?'),
        randomize=True
    ) \
    .display('Thank you, goodbye') \
    .append(testing_a_callback('a','b')) \
    .append(inbox()) \
    .run(client=ReallyDumbTerminal()) \
    .dump_store()