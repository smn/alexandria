import random
import operator

def msg(message, options):
    """
    
    >>> print msg("1 + 1 = ?", ("1", "2"))
    1 + 1 = ?
    1: 1
    2: 2
    >>>
    
    """
    if options:
        message += '\n' + ol(options)
    return message

def ol(list):
    """
    >>> print ol(["a","b","c"])
    1: a
    2: b
    3: c
    >>> 
    
    """
    return '\n'.join('%s: %s' % (idx, item) for idx,item in enumerate(list, start=1))

def shuffle(*items):
    """
    Randomly reorder the items in the list
    """
    items = list(items)
    random.shuffle(items)
    return items


def coroutine(func):
    """
    Grabbed from the pip-0342 examples:
    
        'A simple "consumer" decorator that makes a generator function
        automatically advance to its first yield point when initially
        called'
    
    """
    def start(*args,**kwargs): 
        cr = func(*args,**kwargs) 
        cr.next() 
        return cr
    start.__name__ = func.__name__
    start.__dict__ = func.__dict__
    start.__doc__  = func.__doc__
    return start


def dump_item(item):
    """
    Dump the output of a menu item.
    
    Not guaranteed to always work for all menu items but handy for tests
    nonetheless.
    
    >>> from alexandria.dsl.core import prompt
    >>> from alexandria.dsl.validators import pick_one
    >>> dump_item(prompt('Question?', options=['yes','no']))
    ('Question?\\n1: yes\\n2: no', False)
    >>>
    
    """
    item.next() # manually advance
    return item.send((None, {})) # fake menu system & session store

def dump_menu(menu):
    """
    Dump the output of a menu
    
    Not guaranteed to always work for all menus since it doesn't account
    for any given input.
    
    >>> from alexandria.dsl.core import MenuSystem, prompt, end
    >>> from alexandria.dsl.validators import pick_one
    >>> menu = MenuSystem(
    ...     prompt('Question?', options=['a','b']),
    ...     end('Bye!'))
    >>>
    >>> dump_menu(menu)
    [('Question?\\n1: a\\n2: b', False), ('Bye!', True)]
    """
    return map(dump_item, [item for idx, item in iter(menu) if item])


def table(header, data):
    """
    Print a pretty table for in the console, nice for debugging the state.
    
    >>> print table("Header", {"hello":"world", "foo":"bar"}.items())
    +-----------+
    |   Header  |
    +-----------+
    |foo  |bar  |
    |hello|world|
    +-----------+
    >>> 
    
    """
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
