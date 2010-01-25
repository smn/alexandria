from validators import always_true
from exceptions import InvalidInputException
from utils import msg, consumer
from contextlib import contextmanager

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.stack = [
            prompt('ident')
        ]
        self.storage = {}
    
    def clone(self, **kwargs):
        """Clone self, always return a clone instead of self when chaining
        methods, otherwise you'll get lost of confusing behaviour because
        vars are passed by reference"""
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__ = self.__dict__.copy()
        clone.__dict__.update(kwargs)
        return clone
    
    def store(self, item):
        self.storage[item.request] = item.response
    
    def do(self, *items):
        """Clone the stack and append a batch of items to it"""
        clone = self.clone()
        clone.stack.extend(list(items))
        return clone
    
    def next(self, start_at=0):
        # return current & next items
        return self.stack[start_at], self.stack[start_at + 1]
    
    

class StateKeeper(object):
    def __init__(self, client, menu_system):
        self.index = 0
        self.client = client
        self.menu_system = menu_system
    
    def fast_forward(self, index):
        self.index = index
    
    def has_next(self):
        return self.index <= (len(self.menu_system.stack) - 2)
        
    def next(self):
        current_menu, next_menu = self.menu_system.next(start_at=self.index)
        current_menu.response = self.client.receive() # blocking
        self.menu_system.store(current_menu)
        self.client.send(msg(next_menu.request, next_menu.options))
        self.index = self.index + 1

class prompt(object):
    def __init__(self, request, response=None, validator=always_true, options=()):
        self.request = request
        self.response = response
        self.validator = validator
        self.options = options
    
    def __repr__(self):
        return "%s, %s" % (self.request, self.options)

# def prompt(text, validator=always_true, options=()):
#     return Menu(request=text, validator=validator, options=options)
# 
