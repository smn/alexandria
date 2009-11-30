from statemachine import StateMachine

def coroutine(func): 
    def start(*args,**kwargs): 
        cr = func(*args,**kwargs) 
        cr.next() 
        return cr 
    return start 

@coroutine
def prompt(message):
    while True:
        ms = (yield)
        yield ms.client.read(message)


class ReallyDumbTerminal(object):

    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append

    def display(self, msg):
        print self.format(msg)

    def read(self, msg=''):
        return raw_input(self.format(msg, append='\n<- '))



class MenuSystem(object):
    def __init__(self):
        self.state = []
    
    def callback(self, routine):
        self.state.append(routine)
        return self
    
    def run(self, client):
        self.client = client
        for routine in self.state:
            result = routine.send(self)
            print result
    


ms = MenuSystem()
ms \
    .callback(prompt('hello!')) \
    .callback(prompt('dont know!')) \
    .run(client=ReallyDumbTerminal())