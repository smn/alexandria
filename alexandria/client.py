from alexandria.core import consumer
from alexandria.exceptions import InvalidInputException

class ReallyDumbTerminal(object):
    
    def __init__(self, client_id):
        self.client_id = client_id
    
    def process(self, menu_system):
        for step, coroutine, question in menu_system.run():
            # question might be None if for some reason the coroutine turns
            # out not to need any user info
            if question:
                answer = self.connection().send(question)
                validated_answer = coroutine.send(answer)
                yield step, coroutine, question, validated_answer
            else:
                yield step, coroutine, question, None
            
    
    @consumer
    def introspect(self):
        while True:
            step, coroutine, question, answer = (yield)
            print step, coroutine, question, answer
    
    def format(self, msg, append='\n<- '):
        return '-> ' + '\n-> '.join(msg.split('\n')) + append
    
    @consumer
    def connection(self):
        while True:
            output = yield
            yield raw_input(self.format(output))
    


