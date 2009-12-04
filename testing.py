from hivquiz import *
from alexandria.client import * 

def test():
    while True:
        var = yield 'a'
        print 'var', var
    yield

# client = ReallyDumbTerminal('msisdn')
# gen = client.process(ms)
# for i in ms.run(): print i
