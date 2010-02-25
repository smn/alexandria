from validators import always_true
from exceptions import InvalidInputException
from utils import msg, coroutine
from contextlib import contextmanager
from generator_tools.copygenerators import copy_generator
import types
import logging
from logging.handlers import TimedRotatingFileHandler
import copy

# setup logging, printing everything will make you cross eyed, trust me
logger = logging.getLogger()
logger.name = "alexandria"
logger.level = logging.DEBUG

handler = TimedRotatingFileHandler("logs/alexandria.log", when='midnight', backupCount=14)
handler.setFormatter(logging.Formatter('[%(name)s] %(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)

class MenuSystem(object):
    def __init__(self, *items):
        # a list of items to work through in this menu
        self.stack = list(items)
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
    
    def append(self, *items):
        """Clone the stack and append a batch of items to it"""
        clone = self.clone()
        clone.stack.extend(list(items))
        return clone
    
    def __iter__(self):
        return self
    
    def fast_forward(self, index):
        self.__iter_index = index
    
    def repeat_current_item(self):
        self.fast_forward(self.__iter_index - 1)
        return self.next()
    
    def next_after(self, index):
        self.fast_forward(index)
        return self.next()
    
    def next(self):
        if self.__iter_index > len(self.stack):
            raise StopIteration
        
        if self.__iter_index == len(self.stack):
            next_item = None
        else:
            next_item = copy_generator(self.stack[self.__iter_index])
        self.__iter_index += 1
        return self.__iter_index, next_item


# @coroutine
def prompt(text, validator=always_true, options=()):
    while True:
        ms, session = yield
        question = msg(text, options)
        yield question
        answer = yield
        validated_answer = validator(answer, options)
        session[text] = validated_answer
        yield validated_answer
