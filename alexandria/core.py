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
    
    def has_next(self):
        return self.__iter_index < len(self.stack)
    
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
        yield question, False
        answer = yield
        validated_answer = validator(answer, options)
        session[text] = validated_answer
        yield validated_answer

def end(text):
    while True:
        ms, session = yield
        yield text, True # True is for, yes, end the session - FIXME!

def pick_one(text, options=()):
	return prompt(text, validator=pick_one, options=options)

def question(text, options):
    """

    Example:

        MenuSystem(
            *question('Can traditional medicine cure HIV/AIDS?', {
                'no': 'Correct! Press 1 to continue.',
                'yes': 'Incorrect! Please check your answer and press 1 to continue'
            })
        )

    Is the same as:

        MenuSystem(
            prompt(_('Can traditional medicine cure HIV/AIDS?'), {
                'options': ('yes','no'),
                'validator': pick_one
            }),
            case(
                (
                    lambda (ms, session): session['Can traditional medicine cure HIV/AIDS?'] == ['1']),
                    prompt('Correct! Press 1 to continue.')
                ),
                (
                    lambda (ms, session): session['Can traditional medicine cure HIV/AIDS?'] != ['1']),
                    prompt('Incorrect! Please check your answer and press 1 to continue.')
                ),
            )
        )


    """
    stack_list = []
    question_text = msg(text, options.keys())
    stack_list.append(prompt(text, options=options.keys()))
    case_list = []
    for idx, (option, answer) in enumerate(options.items(),start=1):
        case_list.append(
            (check_answer(question_text, [str(idx)]), prompt(answer))
        )
    stack_list.append(case(*case_list))

