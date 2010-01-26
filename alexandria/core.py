from validators import always_true
from exceptions import InvalidInputException
from utils import msg, coroutine
from contextlib import contextmanager
from generator_tools.copygenerators import copy_generator
import types
import logging
import copy

class MenuSystem(object):
    def __init__(self):
        # a list of items to work through in this menu
        self.stack = []
        self.storage = {}
        self.__iter_index = 0
    
    def clone(self, **kwargs):
        """Clone self, always return a clone instead of self when chaining
        methods, otherwise you'll get lost of confusing behaviour because
        vars are passed by reference"""
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__ = self.__dict__.copy()
        clone.__dict__.update(kwargs)
        return clone
    
    def store(self, key, value):
        self.storage.setdefault(key, []).append(value)
    
    def do(self, *items):
        """Clone the stack and append a batch of items to it"""
        clone = self.clone()
        clone.stack.extend(list(items))
        return clone
    
    def __iter__(self):
        return self
    
    def fast_forward(self, index):
        self.__iter_index = index
    
    def repeat_current_item(self):
        self.__iter_index = self.__iter_index - 1
    
    def next(self):
        # return current & next items
        if self.__iter_index == len(self.stack):
            raise StopIteration
        elif self.__iter_index == 0:
            current = None
            next = copy_generator(self.stack[0])
        elif self.__iter_index == len(self.stack) - 1:
            current = copy_generator(self.stack[-1])
            next = None
        else:
            current = copy_generator(self.stack[self.__iter_index])
            next = copy_generator(self.stack[self.__iter_index + 1])
        self.__iter_index = self.__iter_index + 1
        return current, next
    

# @coroutine
def prompt(text, validator=always_true, options=()):
    while True:
        # yield question
        yield msg(text, options)
        
        # wait for answer
        answer = yield
        yield validator(answer, options)
        # initialize storage as a list if it doesn't exist
        # ms.storage.setdefault(text, [])
        # ms.storage[text].append(validated_answer)
        # yield validated_answer
