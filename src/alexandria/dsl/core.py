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

handler = TimedRotatingFileHandler("logs/alexandria.log", 
                                    interval=1, # every day
                                    when='midnight', # rotate at midnight 
                                    backupCount=14) # keep 14 days worth of logs
handler.setFormatter(logging.Formatter('[%(name)s] %(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)

class MenuSystem(object):
    def __init__(self, *items):
        # a simple linear stack of items to work through
        self.stack = list(items)
        self.__iter_index = 0
    
    def clone(self, **kwargs):
        """
        Clone self, always return a clone instead of self when chaining
        methods, otherwise you'll get lots of confusing behaviour because
        vars are passed by reference
        """
        clone = self.__class__.__new__(self.__class__)
        clone.__iter_index = self.__iter_index
        clone.stack = map(copy_generator, self.stack)
        return clone
    
    def append(self, *items):
        """
        Clone the stack and append *items to it. Appended items need to be
        coroutines.
        """
        self.stack.extend(list(items))
        clone = self.clone()
        return clone
    
    def __iter__(self):
        return self
    
    def get_current_index(self):
        return self.__iter_index
    
    def fast_forward(self, index):
        """
        Fast forward to the given index in the stack.
        
        TODO:   how will we go about this when menu's become tree structures 
                instead of linear paths?
        """
        self.__iter_index = index
    
    def repeat_current_item(self):
        """
        Repeat the current item, decrements the counter by one & calls 
        next() to repeat the current item.
        """
        self.fast_forward(self.__iter_index - 1)
        return self.next()
    
    def next_after(self, index):
        """
        Short hand for returning the next item in the stack
        """
        self.fast_forward(index)
        return self.next()
    
    def next(self):
        """
        Proceed to the next coroutine in the stack
        """
        # If we've reached the end of the stack stop iterating
        if self.__iter_index > len(self.stack):
            raise StopIteration
        
        # If we're at the last time there isn't a next item to send 
        # to the client so return None
        if self.__iter_index == len(self.stack):
            next_item = None
        else:
            # otherwise, copy the coming coroutine, the index is always
            # one ahead of where we are actually at.
            next_item = copy_generator(self.stack[self.__iter_index])
        # increment, ready for next round
        self.__iter_index += 1
        return self.__iter_index, next_item


# TODO:
#
# This var1, var2 = yield stuff is far too magical for every day use.
# We should be looking at ways of abstracting this away from every day
# development. The power of coroutines is in masking blocking I/O
# as non-blocking
#
# We should be able to do the following, this is almost correct pseudo code
# that might actually work but isn't tested yet.
# 
# class Interaction(object):
#     
#     def do(self):
#         """
#         All these processes are blocking processes but coroutines allow us
#         to delay their execution until the client returns.
#         """
#         self.start()
#         self.send_output()
#         self.receive_input()
#     
#     def start(self):
#         self.ms, self.session = yield
#     
#     def send_output(self):
#         yield self.generate_output()
#     
#     def generate_output(self):
#         raise NotImplementedError, "needs to be overriden by subclass"
#     
#     def receive_input(self):
#         _input = yield()
#         yield self.process_input(_input)
#     
#     def process_input(self, _input):
#         raise NotImplementedError, "needs to be overriden by subclass"
# 
# class Prompt(Interaction):
#     
#     def __init__(self, text, options=(), validator=always_true):
#         self.text = text
#         self.options = options
#         self.validator = validator
#     
#     def generate_output(self):
#         """return the output to be sent back to the client"""
#         end_of_session = False # we need to find a way to make this more explicit
#         return msg(self.text, self.options), end_of_session
#     
#     def process_input(self, _input):
#         """process the input received from the client"""
#         validated_answer = self.validator(_input, self.options)
#         self.session[text] = validated_answer
#         return validated_answer
#     
# 

# FIXME: Use @coroutine decorator
def prompt(text, validator=always_true, save_as=None, options=(), parse=False):
    """
    Prompt the user with a question, possibly multiple choice. 
    Read the answer, validate it and store it in the session store.
    """
    save_as = save_as or text
    while True: # allows coroutines to be re-run
        # get menu system & session store
        ms, session = yield
        question = msg(text, options)
        if parse:
            question = question % session
        # return question & boolean indicating end of session
        # FIXME: boolean is ugly
        yield question, False
        # get answer back
        answer = yield
        # validate
        validated_answer = validator(answer, options)
        # store question & validated answer
        session[save_as] = validated_answer
        # return validated answer
        yield validated_answer

def end(text):
    """
    Sign-off the user with the given text. Ends the session
    """
    while True:
        ms, session = yield
        yield text, True # True is for, yes, end the session - FIXME!


def case(*cases):
    """Returns the first prompt for which the test function returns True"""
    while True:
        ms, session = yield
        for test, prompt in cases:
            if test(ms, session):
                prompt = copy_generator(prompt)
                prompt.next()
                question = prompt.send((ms, session))
                yield question
                answer = yield
                prompt.next()
                validated_answer = prompt.send(answer)
                yield validated_answer
        yield False, False # no message and not end of menu


def pick_first_unanswered(*prompts):
    """Returns the first prompt for which the storage doesn't have an
    answer stored yet."""
    cloned_prompts = map(copy_generator, prompts)
    while True:
        ms, session = yield
        while cloned_prompts:
            prompt = cloned_prompts.pop()
            prompt.next()
            question, end_of_session = prompt.send((ms, session))
            if not any([question.startswith(key) for key in session]):
                yield question, end_of_session
                answer = yield
                prompt.next()
                validated_answer = prompt.send(answer)
                yield validated_answer
            else:
                logging.debug('already handled question %s' % question)
        yield False, False # no message and not end of menu


def question(text, options):
    """
    Having python generate prompts & cases for us on the fly. We should probably
    look at ways of doing more of this or making it possible through the DSL.
    
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
    
    # FIXME: this shouldn't be inline once stuff goes into production
    def check_answer(question, answer):
        # this function is returned to the case statement since it requires a 
        # call back and not a result of a function
        def _checker(ms, session):
            return session[question] == answer
        return _checker
    
    
    # temporary stack that is unpacked with python's * operator
    stack_list = []
    # generate the question, need it for checking the answer later on
    question_text = msg(text, options.keys())
    # add prompt to the stack, the keys in the dictionary are the options for the prompt
    stack_list.append(prompt(text, options=options.keys()))
    # temporary stack to store cases
    case_list = []
    # loop over the items to generate the proper case items
    for option, answer in options.items():
        # append the check anwer to the case list
        # if check_answer returns true, return the given prompt
        case_list.append(
            (check_answer(text, option), prompt(answer))
        )
    # append the unpacked case list to the stack list
    stack_list.append(case(*case_list))
    
    return stack_list

