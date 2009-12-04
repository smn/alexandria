from alexandria.core import coroutine
class ReallyDumbTerminal(object):
    
    def __init__(self, client_id):
        self.client_id = client_id
    
    def process(self, menu_system):
        # start the coroutine, returns a generator accepting input
        generator = menu_system.run()
        # first message we send should be some form of client id
        # a way to identify the connecting user in the system
        generator.send(self.client_id)
        # step through the menu_sytem by looping over the generator
        for step, coroutine, question in generator:
            # get the answer to the current question
            answer = self.read().send(question)
            # yield to the client so it can have a look at the current state
            yield step, coroutine, question, answer
            # reply the answer back to the generator so it can continue
            generator.send(answer)
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    @coroutine
    def display(self, msg):
        while True:
            msg = (yield)
            print self.format(msg, append ='')
            yield ''
    
    @coroutine
    def read(self):
        while True:
            msg = (yield)
            yield raw_input(self.format(msg))
    


