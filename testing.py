from alexandria.core import coroutine

@coroutine
def ioloop():
    while True:
        incoming = (yield)
        print 'got incoming', incoming
        outgoing = (yield)
        print 'got outgoing', outgoing
        yield incoming
    


g = ioloop()
for i in range(0,10):
    print g.send(i)
