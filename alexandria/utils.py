import random

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


