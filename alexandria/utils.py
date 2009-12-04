import random
import operator

def msg(message, options):
    if options:
        message += '\n' + ol(options)
    return message

def ol(list):
    """return an ordered list"""
    return '\n'.join('%s: %s' % (idx, item) for idx,item in enumerate(list, start=1))

def shuffle(*items):
    items = list(items)
    random.shuffle(items)
    return items


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


def table(header, data):
    """print a pretty table for in the console"""
    column_widths = {}
    buffer = []
    # grab the first row to count the columns
    for idx in range(0, len(data[0])):
        all_column_widths = [len(str(row[idx])) for row in data]
        column_widths[idx] = max(all_column_widths)
    combined_width = reduce(operator.add, column_widths.values()) + (len(column_widths) - 1)

    buffer.append('+' + ('-' * combined_width) + '+')
    buffer.append('|' + header.center(combined_width) + '|')
    buffer.append('+' + ('-' * combined_width) + '+')
    for row in data:
        padded_columns = [str(column).ljust(column_widths[idx]) for idx, column in enumerate(row)]
        buffer.append('|' + '|'.join(padded_columns) + '|')
    buffer.append('+' + ('-' * combined_width) + '+')
    return '\n'.join(buffer)
